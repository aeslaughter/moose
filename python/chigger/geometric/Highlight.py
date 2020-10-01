import math
import vtk
from .. import utils
from .GeometricSource import GeometricSource, GeometricSource2D

class HighlightBase(object):
    @staticmethod
    def validOptions():
        opt = utils.Options()
        opt.add('color', vtype=utils.AutoColor, doc="The color of the outline")
        opt.add("offset", 0, vtype=(int, float),
                doc="Offset percentage applied to the 3D bounding box")
        opt.add('source', required=True,
                doc='The chigger.base.ChiggerSourceBase object that shall be highlighted')
        return opt

    def _onRequestInformation(self, *args):
        if self.isOptionValid('color'):
            self._vtkactor.GetProperty().SetColor(self.getOption('color').rgb())

class Highlight(GeometricSource, HighlightBase):
    VTKSOURCETYPE = vtk.vtkOutlineCornerSource

    @staticmethod
    def validOptions():
        opt = GeometricSource.validOptions()
        opt += HighlightBase.validOptions()
        return opt

    def __init__(self, **kwargs):
        GeometricSource.__init__(self, nInputPorts=1, inputType='vtkPolyData', **kwargs)
        self.SetInputConnection(self.getOption('source').GetOutputPort())

    def _onRequestInformation(self, *args):
        GeometricSource._onRequestInformation(self, *args)
        HighlightBase._onRequestInformation(self, *args)

    def _onRequestData(self, inInfo, outInfo):
        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        bnds = list(inp.GetBounds())
        offset = self.getOption('offset')
        for i in [1,3,5]:
            dx = bnds[i] - bnds[i-1]
            bnds[i-1] = bnds[i-1] - dx * offset
            bnds[i] = bnds[i] + dx * offset

        self._vtksource.SetBounds(bnds)
        GeometricSource._onRequestData(self, inInfo, outInfo)

class Highlight2D(GeometricSource2D, HighlightBase):
    VTKSOURCETYPE = vtk.vtkOutlineCornerSource

    @staticmethod
    def validOptions():
        opt = GeometricSource2D.validOptions()
        opt += HighlightBase.validOptions()
        return opt

    def __init__(self, **kwargs):
        GeometricSource2D.__init__(self, nInputPorts=1, inputType='vtkPolyData', **kwargs)
        self.SetInputConnection(self.getOption('source').GetOutputPort())

    def _onRequestInformation(self, *args):
        GeometricSource2D._onRequestInformation(self, *args)
        HighlightBase._onRequestInformation(self, *args)

    def _onRequestData(self, inInfo, outInfo):
        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        bnds = list(inp.GetBounds())

        offset = self.getOption('offset')
        for i in [1,3,5]:
            bnds[i-1] = bnds[i-1] - offset
            bnds[i] = bnds[i] + offset

        self._vtksource.SetBounds(bnds)
        GeometricSource2D._onRequestData(self, inInfo, outInfo)
