import vtk
from GeometricSourceBase import GeometricSourceBase

class Outline(GeometricSourceBase):

    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSourceBase.validOptions()
        opt.add('bounds', None, vtype=float, size=6,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax, zmin, zmax].")
        return opt

    def applyOptions(self):
        GeometricSourceBase.applyOptions(self)
        self.assignOption('bounds', self._vtksource.SetBounds)


class Outline2D(GeometricSourceBase):
    VTKACTORTYPE = vtk.vtkActor2D
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D
    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSourceBase.validOptions()
        opt.add('bounds', None, vtype=float, size=4,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax].")
        return opt

    def applyOptions(self):
        GeometricSourceBase.applyOptions(self)
        bnds = self.getOption('bounds')

        # Compute display coordinates
        coord = vtk.vtkCoordinate()
        coord.SetCoordinateSystemToNormalizedViewport()
        coord.SetValue(bnds[0], bnds[2])
        p0 = coord.GetComputedDisplayValue(self._viewport.getVTKRenderer())
        coord.SetValue(bnds[1], bnds[3])
        p1 = coord.GetComputedDisplayValue(self._viewport.getVTKRenderer())

        self._vtksource.SetBounds(p0[0], p1[0], p0[1], p1[1], 0, 0)
