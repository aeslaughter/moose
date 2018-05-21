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
from .. import utils

class KeyPressInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera):
    """
    An interactor style for capturing key press events in VTK window.
    """
    def __init__(self, parent=None, **kwargs):
        self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.keyPress)
        #self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.leftButton)
        #self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.mouseMove)
        super(KeyPressInteractorStyle, self).__init__(parent, **kwargs)

        self.__active = None

    def keyPress(self, obj, event): #pylint: disable=unused-argument
        """
        Executes when a key is pressed.

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetInteractor().GetKeySym()
        if key == 'c':
            print '\n'.join(utils.print_camera(self.GetCurrentRenderer().GetActiveCamera()))

    def leftButton(self, obj, event):

        if self.__active:
            self.__active = None

        else:
            loc = obj.GetInteractor().GetEventPosition()
            r = obj.GetInteractor().FindPokedRenderer(*loc)
            self.__active = r.PickProp(*loc)

    def mouseMove(self, obj, event):

        loc = obj.GetInteractor().GetEventPosition()
        if self.__active:
            for i in range(self.__active.GetNumberOfItems()):
                prop = self.__active.GetItemAsObject(i).GetViewProp()
                prop.SetPosition(0.1,0.1)#*loc)
                print prop
