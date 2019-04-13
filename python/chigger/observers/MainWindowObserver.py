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
import textwrap
import vtk

import mooseutils
from ChiggerObserver import ChiggerObserver
from .. import utils


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
        bindings.add('r', MainWindowObserver._nextResult, desc="Select the next result object.")
        bindings.add('r', MainWindowObserver._previousResult, shift=True,
                     desc="Select the previous result object.")
        bindings.add('t', MainWindowObserver._deactivateResult, desc="Clear selection(s).")
        bindings.add('h', MainWindowObserver._printHelp, desc="Display the help for this object.")
        return bindings

    def __init__(self, *args, **kwargs):
        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        self.__current_actor_index = 0
        #self.__actors = list()

        #window = self.GetInputAlgorithm()
        self._window().getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
                                                      self._onKeyPressEvent)

        #window.getVTKInteractor()._foo = window
        #window.getVTKInteractor().UnRegister(window)

        #window.getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
        #                                      window._onKeyPressEvent)


        #window.getVTKInteractor().AddObserver(vtk.vtkCommand.MouseMoveEvent,
        #                                      self._onMouseMoveEvent)
        #self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent,
        #                                            self._onMouseLeftButtonEvent)

    #    self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.DeleteEvent,
    #                                                self._onDeleteEvent)

    #def RequestData(self, request, inInfo, outInfo):
    #    self.log('RequestData', level=logging.DEBUG)

    #def _onDeleteEvent(self, *args):
    #    print 'delete...'

    def applyOptions(self):
        ChiggerObserver.applyOptions(self)

        #window = self.GetInputAlgorithm()

        #self.__actors = list()
        #for result in window:
        #    for source in result:
        #        self.__actors.append((result, source, source.getVTKActor()))

        #print self, self.__actors, len(self.__actors)

    def _nextResult(self, window, binding): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Activate the "next" result object.
        """

        #window = self.GetInputAlgorithm()
        actors = list()
        for result in self._window():
            for source in result:
                actors.append((result, source, source.getVTKActor()))


        self.__current_actor_index += 1
        if self.__current_actor_index == len(actors):
            self.__current_actor_index = 0

       ## print self, self.__actors, len(self.__actors)

        _, _, actor = actors[self.__current_actor_index]
        self._window().getVTKInteractorStyle().HighlightProp(actor)

    def _previousResult(self, window, binding): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Activate the "previous" result object.
        """
        #self.__current_actor_index -= 1
        #if self.__current_actor_index == -1:
        #    self.__current_actor_index = len(self.__actors) - 1

        #actor = self.__actors[self.__current_actor_index]
        #self._window.getVTKInteractorStyle().HighlightProp(actor)

    def _deactivateResult(self, window, binding): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Deactivate all results.
        """
        window.setActive(None)

    def _printHelp(self, window, binding): #pylint: disable=unused-argument
        """
        Keybinding callback: Display the available controls for this object.
        """

        # Object name/type
        print mooseutils.colorText('General Keybindings:', 'YELLOW')
        self.__printKeyBindings(self.keyBindings())

        active = window.getActive()
        if active is not None:
            print mooseutils.colorText('\n{} Keybindings:'.format(active.title()), 'YELLOW')
            self.__printKeyBindings(active.keyBindings())

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


   # def __del__(self):
        #self.log('__del__()', level=logging.DEBUG)
        # self._window = None
