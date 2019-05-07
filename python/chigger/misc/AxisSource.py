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
from .. import base
from .. import utils
from ..Window import Window

#@Window.addBackgroundOptions('color')
class AxisSource(base.ChiggerSource):
    """
    Creates an Axis with limits, ticks, etc.
    """

    VTKACTORTYPE = vtk.vtkAxisActor2D#vtk.vtkContextActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D#None

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()

        # Font Colors
        opt.add('fontcolor', default=(1,1,1), vtype=float, size=3, doc="The color of the axis, ticks, and labels.")
        #opt.add('axis_fontcolor', vtype=float, size=3, doc="The color of the axis, this overrides the value in 'fontcolor'.")

        opt.add('title', vtype=str, doc="The title for the axis.")
        opt += utils.FontOptions.validOptions('title')


        return opt

    def __init__(self, **kwargs):

        #self._vtksource = vtk.vtkAxis()

        base.ChiggerSource.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)

        #self._vtkactor.GetScene().AddItem(self._vtksource)

    def applyOptions(self):
        """
        Update the vtkAxis with given settings. (override)

        Inputs:
            see ChiggerFilterSourceBase
        """
        base.ChiggerSource.applyOptions(self)

        self._vtkactor.SetPoint1(0.5, 0.1)
        self._vtkactor.SetPoint2(0.5, 0.9)

        self.setOption('title', self._vtkactor.SetTitle)



        if self.isOptionValid('fontcolor'):
            clr = self.getOption('fontcolor')




            #self._vtkactor.GetTitleTextProperty().SetColor(*clr)
            #self._vtkactor.GetTitleTextProperty().SetShadow(False)
            #self._vtkactor.GetTitleTextProperty().SetItalic(False)
            #self._vtkactor.GetLabelTextProperty().SetColor(*clr)
            #self._vtkactor.GetAxisLinesProperty().SetColorF(*clr)



        #self._vtkactor.GetScene().AddItem(self._vtksource)

        #clr = (1,0,1)
        #self._vtksource.GetTitleProperties().SetColor(*clr)
        #self._vtksource.GetLabelProperties().SetColor(*clr)
        #self._vtksource.GetPen().SetColorF(*clr)

        #utils.AxisOptions.setOptions(self._vtksource, self._options)
        #self._vtksource.Update()

    #def getBounds(self):
    #    p0 = self._vtksource.GetPosition1()
    #    p1 = self._vtksource.GetPosition2()
    #    return (p0[0], p1[0], p0[1], p1[1], 0, 0)
