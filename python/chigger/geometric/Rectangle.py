import logging
import vtk
from chigger import base

class Rectangle(base.ChiggerSource):
    VTKACTORTYPE = vtk.vtkActor2D
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper

    def __init__(self, **kwargs):
        base.ChiggerSource.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)


    def RequestData(self, request, inInfo, outInfo):
        pass
