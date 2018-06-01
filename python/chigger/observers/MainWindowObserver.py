#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
from ChiggerObserver import ChiggerObserver
from ..base.ChiggerResultBase import ResultEventHandler
class MainWindowObserver(ChiggerObserver):
    """
    The main means for interaction with the chigger interactive window.
    """

    """
    Notes:
    - Create KeyBinding class here (?) instead of the namedtuple in ChiggerResult base
    - All increments should be <key> for increase and shift-<key> for opposite
    - ChiggerResultBase::AddKeyBinding should compare against reserved items from this object via
      a class variable as well as other items in the self.__keybindings map
    - Help should list the "global" and "local" bindings (i.e., local to the active result)
    - ChiggerObject should have a "name" option that defaults to the class name, this name
      should be used in the key binding dump
    - ChiggerResultBase::getKeyBinding should take a KeyBinding object for lookup
    - ChiggerResultBase::__keybindings should probably just be a set() of KeyBinding objects
    """


    @staticmethod
    def getOptions():
        opt = ChiggerObserver.getOptions()
        return opt

    def __init__(self, **kwargs):
        super(MainWindowObserver, self).__init__(**kwargs)
        self.__selected = None

    def addObservers(self, obj):
        """
        Add the KeyPressEvent for this object.
        """
        obj.AddObserver(vtk.vtkCommand.KeyPressEvent,  self._onKeyPressEvent)
        obj.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self._onLeftButtonPressEvent)
        obj.AddObserver(vtk.vtkCommand.MouseMoveEvent, self._onMouseMoveEvent)

    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the RenderWindow.

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetInteractor().GetKeySym().lower()
        shift = obj.GetInteractor().GetShiftKey()
        control = obj.GetInteractor().GetControlKey()
        alt = obj.GetInteractor().GetAltKey()

        binding = self._window.getActive().getKeyBinding(key, shift, control, alt)
        if binding is not None:
            binding.function(obj, self._window, binding)

        self._window.update()

    def _onLeftButtonPressEvent(self, obj, event):
        loc = obj.GetInteractor().GetEventPosition()
        renderer = self._window.getVTKInteractor().FindPokedRenderer(*loc)
        properties = renderer.PickProp(*loc)
        if properties is not None:
            self.__selected = None
            for result in self._window:
                if renderer is result.getVTKRenderer():
                    result._ResultEventHandler__active = not result._ResultEventHandler__active
                    result.onSelect(result._ResultEventHandler__active)
                    self.__selected = result if result._ResultEventHandler__active else None
                    break
        else:
            self.__selected = None

        self._window.update()

    def _onMouseMoveEvent(self, obj, event):
        if self.__selected is not None:
            loc = obj.GetInteractor().GetEventPosition()
            sz = self.__selected.getVTKRenderer().GetSize()
            position=(loc[0]/float(sz[0]), loc[1]/float(sz[1]))
            self.__selected.onMouseMoveEvent(position)
            #self.__selected.getVTKRenderer().REnd.GetRenderWindow().Render()
            self._window.update()

        #properties = renderer.PickProp(*loc)
        #if properties:
        #    for prop in properties:
        #        self._window.getVTKInteractorStyle().HighlightProp(prop.GetViewProp())
        #        print 'Highlight', type(prop.GetViewProp())
        #else:
        #    for result in self._window.getResults():
        #        actors = result.getVTKRenderer().GetActors()
