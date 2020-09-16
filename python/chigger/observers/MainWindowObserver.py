#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import re
import logging
import weakref
import textwrap
import vtk

import mooseutils
from .ChiggerObserver import ChiggerObserver
from .. import utils
from .. import geometric

class MainWindowObserver(ChiggerObserver, utils.KeyBindingMixin):
    """
    The main means for interaction with the chigger interactive window.
    """
    RE = re.compile(r"(?P<key>[^\s=]+)=(?P<value>.*?)(?=(?:,\s[^\s=]+=|\Z)|\)\Z)")

    @staticmethod
    def validOptions():
        opt = ChiggerObserver.validOptions()
        opt += utils.KeyBindingMixin.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()

        bindings.add('v', MainWindowObserver._nextViewport, desc="Select the next viewport.")
        bindings.add('v', MainWindowObserver._nextViewport, shift=True, args=(True,),
                     desc="Select the previous viewport.")

        bindings.add('s', MainWindowObserver._nextSource,
                     desc="Select the next source in the current viewport.")
        bindings.add('s', MainWindowObserver._nextSource, shift=True, args=(True,),
                     desc="Select the previous source in the current viewport.")

        bindings.add('t', MainWindowObserver._deactivate, desc="Clear selection(s).")
        bindings.add('w', MainWindowObserver._writeChanges, desc="Write the changed settings to the script file.")

        return bindings

    def __init__(self, *args, **kwargs):
        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        self.addObserver(vtk.vtkCommand.KeyPressEvent, self._onKeyPressEvent)

        # Disable interaction by default, but honor user specified interaction
        for viewport in self._getViewports():

            # Viewport
            v_i = viewport.getOption('interactive') if viewport._options.isSetByUser('interactive') else False
            v_h = viewport.getOption('highlight') if viewport._options.isSetByUser('highlight') else v_i
            viewport.setOptions(highlight=v_h, interactive=v_i)

            # Sources
            for source in viewport.sources():
                s_i = source.getOption('interactive') if source._options.isSetByUser('interactive') else False
                s_h = source.getOption('highlight') if source._options.isSetByUser('highlight') else s_i
                source.setOptions(highlight=s_h, interactive=s_i)

                # If the source is active so must be the viewport
                if s_i:
                    viewport.setOptions(highlight=True, interactive=True)

    def _getViewports(self):
        """Complete list of available Viewport objects"""
        return [viewport for viewport in self._window.viewports() if viewport.getOption('layer') > 0]

    def _getActiveViewport(self):
        """Current active (highlighted) Viewport object"""
        for viewport in self._getViewports():
            if viewport.getOption('interactive'):
                return viewport
        return None

    def _setActiveViewport(self, viewport):
        for vp in self._getViewports():
            active = viewport is vp
            vp.setOptions(interactive=active, highlight=active)
            vp.updateInformation()

    def _nextViewport(self, decrease=False): #pylint: disable=no-self-use, unused-argument
        """
        (Keybinding callback)
        Activate the "next" viewport object.
        """
        self.debug('Select Next Viewport')

        # Remove highlighting from the active source.
        self._setActiveSource(None)

        # Determine the index of the Viewport to be set to active
        index = 0
        viewports = self._getViewports()
        current = self._getActiveViewport()
        if current is not None:
            index = viewports.index(current)
            index = index - 1 if decrease else index + 1

        current = viewports[index] if index < len(viewports) else None
        self._setActiveViewport(current)

        self._window.getVTKWindow().Render()

    def _getSources(self):
        """Complete list of available ChiggerSourceBase objects"""
        return [source for viewport in self._getViewports() for source in viewport.sources() if source.getOption('pickable')]

    def _getActiveSource(self):
        """Current active ChiggerSourceBase object"""
        for source in self._getSources():
            if source.getOption('interactive'):
                return source
        return None

    def _setActiveSource(self, source):
        for s in self._getSources():
            active = s is source
            s.setOptions(highlight=active, interactive=active)
            s._viewport.updateInformation()
            s.updateInformation()

    def _nextSource(self, decrease=False):
        """
        Keybinding callback: Activate the "next" source object in the current viewport
        """
        self.debug('Select Next Source')

        # Determine the index of the ChiggerSourceBase to be set to active
        sources = self._getSources()
        current = self._getActiveSource()
        index = 0
        if current is not None:
            index = sources.index(current)
            index = index - 1 if decrease else index + 1

        current = sources[index] if index < len(sources) else None
        self._setActiveSource(current)

        vp = current._viewport if current is not None else None
        self._setActiveViewport(vp)

        self._window.render()

    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the vtkInteractor KeyPressEvent (see init).

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetKeySym().lower()
        shift = obj.GetShiftKey()
        self.debug('Key press: {}, shift={}', key, shift)

        # This objects bindings
        for binding in self.getKeyBindings(key, shift):
            binding.function(self, *binding.args)

        # Call the Window bindings
        for binding in self._window.getKeyBindings(key, shift):
            binding.function(self._window, *binding.args)

        # Viewport options
        viewport = self._getActiveViewport()
        if viewport is not None:
            for binding in viewport.getKeyBindings(key, shift):
                binding.function(viewport, *binding.args)

        # Source options
        source = self._getActiveSource()
        if source is not None:
            for binding in source.getKeyBindings(key, shift):
                binding.function(source, *binding.args)

        self._window.render()

    def _deactivate(self):
        """Remove all interaction seclections"""
        self._setActiveViewport(None)
        self._setActiveSource(None)


    def _writeChanges(self):
        """Write changes directly to the script"""

        source = self._getActiveSource()
        if source is None:
            return

        trace = source._init_traceback[0]
        filename = trace[0]
        line = trace[1]

        output, sub_output = source._options.getNonDefaultOptions()
        def sub_func(match):
            key = match.group('key')
            value = match.group('value')
            if key in output:
                return '{}={}'.format(key, repr(source.getOption(key)))
            return match.group(0)

        with open(filename, 'r') as fid:
            lines = fid.readlines()

        content = self.RE.sub(sub_func, trace[3])
        lines[line-1] = '{}\n'.format(content)

        print(''.join(lines))
