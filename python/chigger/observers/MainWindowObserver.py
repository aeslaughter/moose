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
    class ObjectRef(object):
        def __init__(self, result, source):
            self.__result_weakref = weakref.ref(result)
            self.__source_weakref = weakref.ref(source)

        @property
        def result(self):
            return self.__result_weakref()

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
        bindings.add('r', MainWindowObserver._selectResult, desc="Select the next result object.")
        bindings.add('r', MainWindowObserver._selectResult, shift=True,
                     desc="Select the previous result object.")

        bindings.add('t', MainWindowObserver._deactivateResult, desc="Clear selection(s).")
        bindings.add('h', MainWindowObserver._printHelp, desc="Display the help for this object.")
        return bindings

    def __init__(self, *args, **kwargs):

        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        #window = self.GetInputAlgorithm()
        self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
                                                    self._onKeyPressEvent)

        #window.getVTKInteractor()._foo = window
        #window.getVTKInteractor().UnRegister(window)

        #window.getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
        #                                      window._onKeyPressEvent)


        #window.getVTKInteractor().AddObserver(vtk.vtkCommand.MouseMoveEvent,
        #                                      self._onMouseMoveEvent)
        self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent,
                                                    self._onMouseLeftButtonEvent)

    #def RequestData(self, request, inInfo, outInfo):
    #    self.log('RequestData', level=logging.DEBUG)

    #def _onDeleteEvent(self, *args):
    #    print 'delete...'

        #self.__outline_source = geometric.OutlineSource()
        #self.__current_result_index = 0
        #self.__results = list()
        self.__result_outline_weakref = None#geometric.OutlineSource()
        self.__source_outline_weakref = None#geometric.OutlineSource()


        self.__current_source_index = -1
        self.__sources = list()
        for result in self._window:
            for source in result:
                if result.interactive() and source.interactive():
                    self.__sources.append(MainWindowObserver.ObjectRef(result, source))





    #def applyOptions(self):
     #   ChiggerObserver.applyOptions(self)
     #   self._initializeObjectList()
        #window = self.GetInputAlgorithm()

    def _selectResult(self, window, binding): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Activate the "next" result object.
        """


        # Deactivate current result and source
        current = self.__sources[self.__current_source_index]
        if self.__result_outline_weakref:
            current.result._remove(self.__result_outline_weakref())
            current.result._remove(self.__source_outline_weakref())

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
        current.result._add(geometric.OutlineSource(bounds=bounds))
        self.__result_outline_weakref = weakref.ref(current.result._sources[-1])

        bounds = current.source.getVTKMapper().GetBounds()
        current.result._add(geometric.OutlineSource(bounds=bounds))
        self.__source_outline_weakref = weakref.ref(current.result._sources[-1])

        self._window.getVTKWindow().Render()



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

        self._window.getVTKWindow().Render()


    def _printHelp(self, window, binding): #pylint: disable=unused-argument
        """
        Keybinding callback: Display the available controls for this object.
        """

        # Object name/type
        print mooseutils.colorText('General Keybindings:', 'YELLOW')
        self.__printKeyBindings(self.keyBindings())

        current = self.__sources[self.__current_source_index]
        if self.__result_outline_weakref:
            print mooseutils.colorText('Current Result Keybindings:', 'YELLOW')
            self.__printKeyBindings(current.result.keyBindings())

        if self.__source_outline_weakref:
            print mooseutils.colorText('Current Source Keybindings:', 'YELLOW')
            self.__printKeyBindings(current.source.keyBindings())

        #active = window.getActive()
        #if active is not None:
        #    print mooseutils.colorText('\n{} Keybindings:'.format(active.title()), 'YELLOW')
        #    self.__printKeyBindings(active.keyBindings())

    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the vtkInteractor KeyPressEvent (see init).

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetKeySym().lower()
        shift = obj.GetShiftKey()

        # This objects bindings
        for binding in self.getKeyBindings(key, shift):
            binding.function(self, self.GetInputAlgorithm(), binding)

        current = self.__sources[self.__current_source_index]
        if self.__result_outline_weakref:
            for binding in current.result.getKeyBindings(key, shift):
                binding.function(self, self._window, binding)


        #if False:#self.__current_active_actor:
        #    result, source = self.__source_result_lookup[self.__current_active_actor]

        #    # ChiggerResult bindings
        #    for binding in result:
        #        binding.function(self, self._window, binding)

        #    # ChiggerSource bindings
        #    for binding in source:
        #        binding.function(self, self._window, binding)


    def _onMouseMoveEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the vtkInteractor MouseMoveEvent (see init)
        """
        #print '_onMouseMoveEvent', obj, event

        """
        result = self._window.getActive()
        if (result is not None) and hasattr(result, 'onMouseMoveEvent'):
            loc = obj.GetEventPosition()
            sz = result.getVTKRenderer().GetSize()
            position = (loc[0]/float(sz[0]), loc[1]/float(sz[1]))
            result.onMouseMoveEvent(position)
            #self._window.update()
        """

    def _onMouseLeftButtonEvent(self, obj, event):
        print '_onMouseLeftButtonEvent'#, obj, event

    @staticmethod
    def __printKeyBindings(bindings):
        """
        Helper for printing keybindings.
        """
        n = 0
        out = []
        for key, value in bindings.iteritems():
            tag = 'shift-{}'.format(key[0]) if key[1] else key[0]
            desc = [item.description for item in value]
            out.append([tag, '\n\n'.join(desc)])
            n = max(n, len(tag))

        for key, desc in out:
            key = mooseutils.colorText('{0: >{w}}: '.format(key, w=n), 'GREEN')
            print '\n'.join(textwrap.wrap(desc, 100, initial_indent=key,
                                          subsequent_indent=' '*(n + 2)))
