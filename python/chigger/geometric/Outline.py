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
        opt.add('bounds', None, vtype=float, size=6,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax].")
        return opt

    def applyOptions(self):
        GeometricSourceBase.applyOptions(self)
        self.assignOption('bounds', self._vtksource.SetBounds)
