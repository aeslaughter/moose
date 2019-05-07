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

    __FONTKEYS__ = utils.FontOptions.validOptions().keys()

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()

        # Font Colors
        opt += utils.FontOptions.validOptions()

        opt.add('title', vtype=str, doc="The title for the axis.")
        opt += utils.FontOptions.validOptions('title')

        opt += utils.FontOptions.validOptions('label')
        #opt += utils.FontOptions.validOptions('axis')

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

        for name in self.__FONTKEYS__:
            for subname in ['title', 'label']:
                tname = '{}_{}'.format(subname, name)
                if not self.isOptionValid(tname):
                    self._options.set(tname, self._options.get(name))

        utils.FontOptions.applyOptions(self._vtkactor.GetTitleTextProperty(), self._options, 'title')
        utils.FontOptions.applyOptions(self._vtkactor.GetLabelTextProperty(), self._options, 'label')

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
