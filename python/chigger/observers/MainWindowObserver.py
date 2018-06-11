#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import textwrap
import vtk

import mooseutils
from ChiggerObserver import ChiggerObserver
from .. import utils
from ..geometric import OutlineResult

class MainWindowObserver(ChiggerObserver, utils.KeyBindingMixin):
    """
    The main means for interaction with the chigger interactive window.
    """

    @staticmethod
    def validOptions():
        opt = ChiggerObserver.validOptions()
        return opt

    def __init__(self, **kwargs):
        super(MainWindowObserver, self).__init__(**kwargs)

        self.addKeyBinding('r', self._nextResult, desc="Select the next result object.")
        self.addKeyBinding('r', self._previousResult, shift=True, desc="Select the previous result object.")
        self.addKeyBinding('d', self._deactivateResult, desc="Clear selection(s).")
        self.addKeyBinding('h', self._printHelp, desc="Display the help for this object.")
        self.addKeyBinding('c', self._printCamera, desc="Display the camera settings for this object.")

        self.__outline_result = None

    def addObservers(self, obj):
        """
        Add the KeyPressEvent for this object.
        """
        obj.AddObserver(vtk.vtkCommand.KeyPressEvent,  self._onKeyPressEvent)
       # obj.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self._onLeftButtonPressEvent)
        obj.AddObserver(vtk.vtkCommand.MouseMoveEvent, self._onMouseMoveEvent)
       # obj.AddObserver(vtk.vtkCommand.WindowResizeEvent, self._onWindowResizeEvent)

#    def isSelected(self):
#        return self.__selected
#
#    def selectResult(self, result):
#        print result


#    def onActivate(self, result, active):
#
#        if active and (self.__outline_result is None):
#            mooseutils.mooseMessage('Activate {}'.format(result.title()))
#            self.__outline_result = OutlineResult(result, color=(1,0,0), edge_width=3, interactive=False)
#            self._window.append(self.__outline_result)
#
#        elif not active and (self.__outline_result is not None):
#            mooseutils.mooseMessage('Deactivate {}'.format(result.title()))
#            self._window.remove(self.__outline_result)
#            self.__outline_result = None

    def onMouseMoveEvent(self, position):
        pass

    def printOption(self, opt):
        print '{}: setOptions({}={})'.format(self.title(), opt, repr(self.getOption(opt)))


    # TODO: Move these to MainWindowObserver



    def _nextResult(self, window, binding):
        self._deactivateResult(window, binding)
        window.nextActive(1)
        window.getActive().onActivate(window, True)

    def _previousResult(self, window, binding):
        self._deactivateResult(window, binding)
        window.nextActive(-1)
        window.getActive().onActivate(window, True)

    def _deactivateResult(self, window, binding):
        active = window.getActive()
        if active is not None:
            active.onActivate(window, False)
        window.setActive(None)

    def _printCamera(self, *args):
        print '\n'.join(utils.print_camera(self._vtkrenderer.GetActiveCamera()))

    def _printHelp(self, window, binding):
        """
        Display the available controls for this object.
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
        n = 0
        out = []
        for key, value in bindings.iteritems():
            tag = 'shift-{}'.format(key[0]) if key[1] else key[0]
            desc = [item.description for item in value]
            out.append([tag, '\n\n'.join(desc)])
            n = max(n, len(tag))

        for key, desc in out:
            key = mooseutils.colorText('{0: >{w}}: '.format(key, w=n), 'GREEN')
            print '\n'.join(textwrap.wrap(desc, 100, initial_indent=key, subsequent_indent=' '*(n + 2)))


    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the RenderWindow.

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetInteractor().GetKeySym().lower()
        shift = obj.GetInteractor().GetShiftKey()

        #for binding in self._window.getActive().getKeyBindings(key, shift):
        for binding in self.getKeyBindings(key, shift):
            binding.function(self._window, binding)

        active = self._window.getActive()
        if active:
            for binding in active.getKeyBindings(key, shift):
                binding.function(self._window, binding)

        self._window.update()

    def _onLeftButtonPressEvent(self, obj, event):
        pass
        """
        loc = obj.GetInteractor().GetEventPosition()
        renderer = self._window.getVTKInteractor().FindPokedRenderer(*loc)
        properties = renderer.PickProp(*loc)
        if properties is not None:
            for result in self._window:
                if renderer is result.getVTKRenderer():
                    self.selectResult(result)
                    #result._ResultEventHandler__selected = not result._ResultEventHandler__selected
                    #result.onSelect(result._ResultEventHandler__selected)
                    break
        self._window.update()
        """
    def _onMouseMoveEvent(self, obj, event):
        result = self._window.getActive()
        if result is not None:
            loc = obj.GetInteractor().GetEventPosition()
            sz = result.getVTKRenderer().GetSize()
            position=(loc[0]/float(sz[0]), loc[1]/float(sz[1]))
            result.onMouseMoveEvent(position)
        self._window.update()

    def _onWindowResizeEvent(self, obj, event):
        pass
        #TODO: vtk8 is needed for this event
        #print obj, event

        #properties = renderer.PickProp(*loc)
        #if properties:
        #    for prop in properties:
        #        self._window.getVTKInteractorStyle().HighlightProp(prop.GetViewProp())
        #        print 'Highlight', type(prop.GetViewProp())
        #else:
        #    for result in self._window.getResults():
        #        actors = result.getVTKRenderer().GetActors()
