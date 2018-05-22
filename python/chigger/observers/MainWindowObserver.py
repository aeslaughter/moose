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
        print 'Pressed:', key

        if key == 'left':
            self._window.nextActive(1)
            print 'Interactive:', self._window.getActive().getVTKRenderer().GetInteractive()
            #self._window.getActive().getVTKRenderer().SetBackground(0.5, 0.5, 0.5)
            #self._window.getActive().getVTKRenderer().Render()
            #print 'alpha = ', self._window.getActive().getVTKRenderer().GetBackgroundAlpha()

            #self._window.getActive().getVTKRenderer().SetBackgroundAlpha(0.5)

        elif key == 'right':
            self._window.nextActive(-1)




    def _onLeftButtonPressEvent(self, obj, event):
        pass
        #loc = obj.GetInteractor().GetEventPosition()
        #renderer = self._window.getVTKInteractor().FindPokedRenderer(*loc)
        #properties = renderer.PickProp(*loc)
        #print properties
