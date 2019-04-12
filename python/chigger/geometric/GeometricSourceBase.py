import logging
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import base


class GeometricSourceBase(base.ChiggerSource, VTKPythonAlgorithmBase):
    """Base class for geometric objects that are passed into ChiggerResult objects."""

    VTKACTORTYPE = vtk.vtkActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper

    #: The underlying VTK type, this should be set by the child class.
    VTKSOURCETYPE = None

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()
        return opt

    def __init__(self, **kwargs):
        self._vtksource = self.VTKSOURCETYPE()

        base.ChiggerSource.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=0, nOutputPorts=1,
                                        outputType='vtkPolyData')


    def RequestData(self, request, inInfo, outInfo):
        self.log('RequestData', level=logging.DEBUG)

        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())

        self._vtksource.Update()
        opt.ShallowCopy(self._vtksource.GetOutput())
        return 1
