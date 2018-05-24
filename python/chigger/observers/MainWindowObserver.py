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

    def addObservers(self, obj):
        """
        Add the KeyPressEvent for this object.
        """
        obj.AddObserver(vtk.vtkCommand.KeyPressEvent,  self._onKeyPressEvent)
        obj.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self._onLeftButtonPressEvent)

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

        if key == 'left':
            self._window.nextActive(1)

        elif key == 'right':
            self._window.nextActive(-1)

        elif key == 'h':
            print 'Help...'

        binding = self._window.getActive().getKeyBinding(key, shift, control, alt)
        if binding is not None:
            binding.function(obj, key, shift, control, alt)

        self._window.update() # Do this only if needed, will applyOption get rid of the NeedsUpdate stuff

    def _onLeftButtonPressEvent(self, obj, event):
        pass
        #loc = obj.GetInteractor().GetEventPosition()
        #renderer = self._window.getVTKInteractor().FindPokedRenderer(*loc)
        #properties = renderer.PickProp(*loc)
        #print properties
