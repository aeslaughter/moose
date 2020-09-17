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
import copy
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

        self._window.render()

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

        # Remove active viewport
        self._setActiveViewport(None)

        # Determine the index of the ChiggerSourceBase to be set to active
        sources = self._getSources()
        current = self._getActiveSource()
        index = 0
        if current is not None:
            index = sources.index(current)
            index = index - 1 if decrease else index + 1

        current = sources[index] if index < len(sources) else None
        self._setActiveSource(current)

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
        """Write changes directly to the script, if desired"""

        # Determine the object to glean options from and error if two things are active
        source = self._getActiveSource()
        viewport = self._getActiveViewport()
        if (source is not None) and (viewport is not None):
            self.error("Both a source and viewport are active which is not supported for writing, because of potential output conflicts.")
            return
        elif (source is None) and (viewport is None):
            self.warning("No active source of viewport to inspect for option changes, so there is nothing to write.")
            return

        # Extract the option information
        obj = source or viewport
        trace = obj._init_traceback[0]
        filename = trace[0]
        line = trace[1]

        # Inline function for swapping options
        output, sub_output = obj._options.getNonDefaultOptions()
        def sub_func(match):
            key = match.group('key')
            value = match.group('value')
            if key in output:
                return '{}={}'.format(key, repr(obj.getOption(key)))
            return match.group(0)

        # Read the original file
        with open(filename, 'r') as fid:
            lines = fid.readlines()

        # Swap line with new option(s)
        content = self.RE.sub(sub_func, trace[3])
        new_lines = copy.copy(lines)
        new_lines[line-1] = '{}\n'.format(content)

        # Create and show the diff, if it exists
        diff = mooseutils.text_unidiff('\n'.join(new_lines), '\n'.join(lines), out_fname=filename, gold_fname=filename, num_lines=1)
        if not diff:
            self.info("No changes to the filename {} to write.", filename)
            return

        # Show the proposed changes
        n = max(max([len(l) for l in lines]), max([len(l) for l in new_lines]))
        print('='*n)
        print('{} PROPOSED CHANGES'.format(filename))
        print('='*n)
        print(diff.strip('\n'))

        # Prompt the user for
        self._window.getVTKInteractor().Disable()
        choice = input("Would you like to overwrite[w], create a diff[d], or quit[q]? ")
        self._window.getVTKInteractor().Enable()

        if choice == 'd':
            with open(filename + '.diff', 'w') as fid:
                fid.write(diff)
        elif choice == 'w':
            with open(filename, 'w') as fid:
                fid.write(''.join(new_lines))
