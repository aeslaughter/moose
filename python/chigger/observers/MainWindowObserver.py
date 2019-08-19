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


#TODO: result -> viewport


class MainWindowObserver(ChiggerObserver, utils.KeyBindingMixin):
    """
    The main means for interaction with the chigger interactive window.
    """

    class ObjectRef(object):
        """
        Helper object for storing result/source information. weakref is used to avoid this
        class taking ownership of objects which can cause VTK to seg. fault.
        """
        def __init__(self, viewport, source):
            self.__viewport_weakref = weakref.ref(viewport)
            self.__source_weakref = weakref.ref(source)

        @property
        def viewport(self):
            return self.__viewport_weakref()

        @property
        def source(self):
            return self.__source_weakref()

        @property
        def actor(self):
            return self.source.getVTKActor()

    @staticmethod
    def validOptions():
        opt = ChiggerObserver.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        bindings.add('v', MainWindowObserver._selectViewport, desc="Select the next viewport.")
        bindings.add('v', MainWindowObserver._selectViewport, shift=True,
                     desc="Select the previous viewport.")

        bindings.add('t', MainWindowObserver._deactivateResult, desc="Clear selection(s).")
        bindings.add('h', MainWindowObserver._printHelp, desc="Display the help for this object.")
        return bindings

    def __init__(self, *args, **kwargs):

        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
                                                    self._onKeyPressEvent)

        #self.__viewport_outline_weakref = None
        #self.__source_outline_weakref = None
        self.__current_viewport_index = None
        self.__current_viewport_outline = None
        #self.__sources = list()]
        #self.__current_index = None


    """
    def _initializeSources(self):

        if self.__current_source_index is not None:
            return

        self.__current_source_index = -1
        self.__sources = list()
        for result in self._window:
            for source in result:
                if result.interactive() and source.interactive():
                    self.__sources.append(MainWindowObserver.ObjectRef(result, source))
    """

    def _selectViewport(self, window, binding): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Activate the "next" result object.
        """
        self.log('Select Viewport', level=logging.DEBUG)

        if self.__current_viewport_outline is not None:
            self.__current_viewport_outline.remove()
            self.__current_viewport_outline = None

        N = len(window.viewports())
        if self.__current_viewport_index is None:
            self.__current_viewport_index = N - 1 if binding.shift else 0
        elif binding.shift:
            self.__current_viewport_index -= 1
            if self.__current_viewport_index < 0:
                self.__current_viewport_index = None
        else:
            self.__current_viewport_index += 1
            if self.__current_viewport_index == N:
                self.__current_viewport_index = None


        if self.__current_viewport_index is not None:
            viewport = window.viewports()[self.__current_viewport_index]
            self.__current_viewport_outline = geometric.Outline2D(viewport,
                                                                  bounds=(0,1,0,1),
                                                                  color=(1, 1, 0), linewidth=6)
        """
        # Deactivate current result and source
        current = self.__sources[self.__current_source_index]
        if self.__result_outline_weakref:
            pass
            #current.result._remove(self.__result_outline_weakref())
            #urrent.result._remove(self.__source_outline_weakref())

        if binding.shift:
            self.__current_source_index -= 1
            if self.__current_source_index == -1:
                self.__current_source_index = len(self.__sources) - 1
        else:
            self.__current_source_index += 1
            if self.__current_source_index == len(self.__sources):
                self.__current_source_index = 0

        current = self.__sources[self.__current_source_index]

        bounds = current.result.getVTKRenderer().ComputeVisiblePropBounds()
        geometric.Outline(current.result, bounds=bounds)
        self.__result_outline_weakref = weakref.ref(current.result._sources[-1])

        bounds = current.source.getBounds()
        geometric.Outline(current.result, bounds=bounds)
        self.__source_outline_weakref = weakref.ref(current.result._sources[-1])
        """
        window.Update()
        window.getVTKWindow().Render()
        #viewport.getVTKRenderer().Render()

    def _deactivateResult(self, window, binding): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Deactivate all results.
        """
        current = self.__sources[self.__current_source_index]
        if self.__result_outline_weakref:
            current.result._remove(self.__result_outline_weakref())
            current.result._remove(self.__source_outline_weakref())
            self.__result_outline_weakref = None
            self.__source_outline_weakref = None

        self._window.Update()

    def _printHelp(self, window, binding): #pylint: disable=unused-argument
        """
        Keybinding callback: Display the available controls for this object.
        """

        # Object name/type
        print mooseutils.colorText('General Keybindings:', 'YELLOW')
        self.printKeyBindings(self.keyBindings())

        if self.__current_viewport_index is not None:
            viewport = window.viewports()[self.__current_viewport_index]
            print mooseutils.colorText('Current Viewport Keybindings ({}):'.format(viewport.name()), 'YELLOW')
            self.printKeyBindings(viewport.keyBindings())

        #if self.__source_outline_weakref:
        #    print mooseutils.colorText('Current Source Keybindings ({}):'.format(current.source.getOption('name')), 'YELLOW')
        #    self.printKeyBindings(current.source.keyBindings())

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
            binding.function(self, self._window, binding)

        """
        current = self.__sources[self.__current_source_index]
        if self.__result_outline_weakref:
            for binding in current.result.getKeyBindings(key, shift):
                binding.function(current.result, self._window, binding)

        if self.__source_outline_weakref:
            for binding in current.source.getKeyBindings(key, shift):
                binding.function(current.source, self._window, binding)
        """
