import math
import vtk
from .GeometricSource import GeometricSource, GeometricSource2D

class Highlight(GeometricSource):
    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSource.validOptions()
        opt.add("offset", 0, vtype=float,
                doc="Offset percentage applied to the 3D bounding box")
        return opt

    def __init__(self, viewport, source, **kwargs):
        GeometricSource.__init__(self, viewport,
                      nInputPorts=1, inputType='vtkPolyData',
                      **kwargs)
        self.SetInputConnection(source.GetOutputPort())

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

class Highlight2D(GeometricSource2D):
    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSource2D.validOptions()
        opt.add("offset", 0, vtype=float,
                doc="Absolute offset, in relative coordinates, applied to the 2D object bounding box")
        return opt

    def __init__(self, viewport, source, **kwargs):
        GeometricSource2D.__init__(self, viewport,
                      nInputPorts=1, inputType='vtkPolyData',
                      **kwargs)
        self.SetInputConnection(source.GetOutputPort())

    def _onRequestData(self, inInfo, outInfo):
        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        bnds = list(inp.GetBounds())

        offset = self.getOption('offset')
        for i in [1,3,5]:
            bnds[i-1] = bnds[i-1] - offset
            bnds[i] = bnds[i] + offset

        self._vtksource.SetBounds(bnds)
        GeometricSource2D._onRequestData(self, inInfo, outInfo)
