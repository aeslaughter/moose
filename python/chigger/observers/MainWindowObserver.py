#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import logging
import weakref
import textwrap
import vtk

import mooseutils
from ChiggerObserver import ChiggerObserver
from .. import utils
from .. import geometric

class MainWindowObserver(ChiggerObserver, utils.KeyBindingMixin):
    """
    The main means for interaction with the chigger interactive window.
    """
    @staticmethod
    def validOptions():
        opt = ChiggerObserver.validOptions()
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
        bindings.add('h', MainWindowObserver._printHelp, desc="Display the help for this object.")
        return bindings

    def __init__(self, *args, **kwargs):

        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
                                                    self._onKeyPressEvent)

        self.__current_viewport_index = None
        self.__current_viewport_outline = None

        self.__current_source_index = None
        self.__current_source_outline = None

    def _availableViewports(self):
        return [viewport for viewport in self._window.viewports() if viewport.interactive]

    def _availableSources(self, viewport):
        return [source for viewport in viewport.sources() if viewport.interactive]

    def _nextViewport(self, decrease=False): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Activate the "next" viewport object.
        """
        self.log('Select Viewport', level=logging.DEBUG)

        if self.__current_viewport_outline is not None:
            self.__current_viewport_outline.remove()
            self.__current_viewport_outline = None

        viewports = self._availableViewports()
        N = len(viewports)
        if self.__current_viewport_index is None:
            self.__current_viewport_index = N - 1 if decrease else 0
        elif decrease:
            self.__current_viewport_index -= 1
            if self.__current_viewport_index < 0:
                self.__current_viewport_index = None
        else:
            self.__current_viewport_index += 1
            if self.__current_viewport_index == N:
                self.__current_viewport_index = None

        if self.__current_viewport_index is not None:
            viewport = viewports[self.__current_viewport_index]
            self.__current_viewport_outline = geometric.Outline2D(viewport,
                                                                  bounds=(0,1,0,1),
                                                                  color=(1, 1, 0), linewidth=6)

    def _nextSource(self, decrease=False):
        """
        Keybinding callback: Activate the "next" source object in the current viewport
        """
        self.log('Select Source', level=logging.DEBUG)

        if self.__current_viewport_outline is None:
            return

        if self.__current_source_outline is not None:
            self.__current_source_outline.remove()
            self.__current_source_outline = None

        viewport = self._avaialbleViewports()[self.__current_viewport_index]
        N = len(viewport)
        if self.__current_source_index is None:
            self.__current_source_index = N - 1 if decrease else 0
        elif decrease:
            self.__current_source_index -= 1
            if self.__current_source_index < 0:
                self.__current_source_index = None
        else:
            self.__current_source_index += 1
            if self.__current_source_index == N:
                self.__current_source_index = None

        if self.__current_source_index is not None:
            source = self._availableSources(viewport)[self.__current_source_index]
            bnds = source.getBounds()
            if len(bnds) == 4:
                self.__current_source_outline = geometric.Outline2D(viewport,
                                                                    bounds=bnds,
                                                                    color=(1, 0, 0), linewidth=6)
            else:
                self.__current_source_outline = geometric.Outline(viewport,
                                                                  bounds=bnds,
                                                                  color=(1, 0, 0), linewidth=6)


    def _deactivate(self): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Deactivate all results.
        """
        if self.__current_viewport_outline is not None:
            self.__current_viewport_outline.remove()
            self.__current_viewport_outline = None

        if self.__current_source_outline is not None:
            self.__current_source_outline.remove()
            self.__current_source_outline = None

    def _printHelp(self): #pylint: disable=unused-argument
        """
        Keybinding callback: Display the available controls for this object.
        """

        # Object name/type
        print mooseutils.colorText('General Keybindings:', 'YELLOW')
        self.printKeyBindings(self.keyBindings())

        if self.__current_viewport_index is not None:
            viewport = self._window.viewports()[self.__current_viewport_index]
            print mooseutils.colorText('Current Viewport Keybindings ({}):'.format(viewport.name()), 'YELLOW')
            self.printKeyBindings(viewport.keyBindings())

        if self.__current_source_index is not None:
            viewport = self._window.viewports()[self.__current_viewport_index]
            source = viewport.sources()[self.__current_source_index]
            print mooseutils.colorText('Current Source Keybindings ({}):'.format(viewport.name()), 'YELLOW')
            self.printKeyBindings(source.keyBindings())

    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the vtkInteractor KeyPressEvent (see init).

        Inputs:
            obj, event: Required by VTK.
        """
        #self._initializeSources()
        key = obj.GetKeySym().lower()
        shift = obj.GetShiftKey()

        # This objects bindings
        for binding in self.getKeyBindings(key, shift):
            binding.function(self, *binding.args)

        # Viewport options
        if self.__current_viewport_index is not None:
            viewport = self._availableViewports()[self.__current_viewport_index]
            for binding in viewport.getKeyBindings(key, shift):
                binding.function(viewport, *binding.args)

        # Source options
        if self.__current_source_index is not None:
            viewport = self._availableViewports()[self.__current_viewport_index]
            source = self._availableSources(viewport)[self.__current_source_index]
            for binding in source.getKeyBindings(key, shift):
                binding.function(source, *binding.args)

        self._window.Update()
        self._window.getVTKWindow().Render()
