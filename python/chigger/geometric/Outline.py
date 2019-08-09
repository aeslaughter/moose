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

        opt.add('coordinate_system', 'normalized_viewport', vtype=str,
                allow=('normalized_viewport', 'viewport'), doc="Set the input coordinate system.")

        return opt

    def applyOptions(self):
        GeometricSourceBase.applyOptions(self)
        bnds = self.getOption('bounds')

        # TODO: This shows up in both the Rectangle (need GeometricSourceBase2D)
        if self._vtkmapper.GetTransformCoordinate() is None:
            self._vtkmapper.SetTransformCoordinate(vtk.vtkCoordinate())
        coordinate = self._vtkmapper.GetTransformCoordinate()
        if self.getOption('coordinate_system') == 'normalized_viewport':
            coordinate.SetCoordinateSystemToNormalizedViewport()
        else:
            coordinate.SetCoordinateSystemToViewport()

        self._vtksource.SetBounds(bnds[0], bnds[1], bnds[2], bnds[3], 0, 0)
