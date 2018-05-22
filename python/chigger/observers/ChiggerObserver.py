#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
from chigger.base import ChiggerObject
class ChiggerObserver(ChiggerObject):
    """
    Base class for definning VTK observer functions.

    This object is a base class and not intended for general use, see TimerObserver as an example.
    """
    @staticmethod
    def getOptions():
        opt = ChiggerObject.getOptions()
        return opt

    def __init__(self, **kwargs):
        super(ChiggerObserver, self).__init__(**kwargs)
        self._window = None

    def addObservers(self, obj):
        """
        Add the observer to the supplied vtkInteractor, see TimerObserver for an example.

        Generally, this method is not needed. If you are creating a new Observer it should inherit
        from one of the existing objects: e.g., KeyObserver, TimerObserver.

        Inputs:
            obj[vtkInteractorStyle]: The interactor that the observer should be added.

        NOTE: This method must return the VTK id return from the AddObserver method.
        """
        raise NotImplementedError("The addObserver method must be implmented.")

    def init(self, window):
        """
        Initialize the observer, this is called by the RenderWindow automatically.

        NOTE: This is an internal method, do not call it.
        """
        self._window = window
        self.addObservers(self._window.getVTKInteractorStyle())
        #self._vtk_command = window.getVTKInteractor().GetCommand(vtkid)
