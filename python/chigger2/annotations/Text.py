#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
#pylint: enable=missing-docstring
import vtk
from .. import base, utils

@base.backgroundOptions('color')
class Text(base.ChiggerSource):
    """
    Result object for adding text to window.
    """
    VTKACTORTYPE = vtk.vtkTextActor
    #VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D


    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()
        opt += utils.TextOptions.validOptions()
        opt.add('text', vtype=str, doc="The text to display.")
        opt.add('position', vtype=float, size=2, doc="The text position in normalized viewport coordinates.")
        return opt

    def __init__(self, text=None, **kwargs):
        base.ChiggerSource.__init__(self, text=text, **kwargs)
        self._vtkactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()

    def applyOptions(self):
        base.ChiggerSource.applyOptions(self)

        self.assignOption('text', self._vtkactor.SetInput)

        utils.TextOptions.applyOptions(self._vtkactor.GetTextProperty(), self._options)

        self.assignOption('position', self._vtkactor.SetPosition)
