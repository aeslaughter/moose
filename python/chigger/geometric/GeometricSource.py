import vtk
from chigger import base


class GeometricSource(base.ChiggerSource):
    """Base class for geometric objects that are passed into ChiggerResult objects."""

    VTKACTORTYPE = vtk.vtkActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper

    #: The underlying VTK type, this should be set by the child class.
    VTKSOURCETYPE = None

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()
        return opt

    def __init__(self, *args, **kwargs):
        self._vtksource = self.VTKSOURCETYPE()
        base.ChiggerSource.__init__(self, *args,
                                    nOutputPorts=1, outputType='vtkPolyData',
                                    **kwargs)

    def RequestData(self, request, inInfo, outInfo):
        super(GeometricSource, self).RequestData(request, inInfo, outInfo)
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        self._vtksource.Update()
        opt.ShallowCopy(self._vtksource.GetOutput())
        return 1

class GeometricSource2D(GeometricSource):
    VTKACTORTYPE = vtk.vtkActor2D
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D
