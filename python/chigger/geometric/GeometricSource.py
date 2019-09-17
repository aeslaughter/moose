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


    def zoom(self, factor):

        origin = self._vtksource.GetOrigin()
        self._vtksource.SetOrigin([origin[0] + factor, origin[1] + factor, 0])

        p = self._vtksource.GetPoint1()
        self._vtksource.SetPoint1([p[0] + factor, p[1] - factor, 0])

        p = self._vtksource.GetPoint2()
        self._vtksource.SetPoint2([p[0] - factor, p[1] + factor, 0])

    def move(self, dx, dy):

        origin = self._vtksource.GetOrigin()
        self._vtksource.SetOrigin([origin[0] + dx, origin[1] + dy, 0])

        p = self._vtksource.GetPoint1()
        self._vtksource.SetPoint1([p[0] + dx, p[1] + dy, 0])

        p = self._vtksource.GetPoint2()
        self._vtksource.SetPoint2([p[0] + dx, p[1] + dy, 0])
