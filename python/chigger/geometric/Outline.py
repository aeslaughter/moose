import vtk
from .GeometricSource import GeometricSource, GeometricSource2D

class Outline(GeometricSource):

    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSource.validOptions()
        opt.add('bounds', None, vtype=float, size=6,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax, zmin, zmax].")
        return opt

    def _onRequestInformation(self):
        GeometricSource._onRequestInformation(self)
        self.assignOption('bounds', self._vtksource.SetBounds)


class Outline2D(GeometricSource2D):
    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSource2D.validOptions()
        opt.add('bounds', None, vtype=float, size=4,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax].")

        return opt

    def _onRequestInformation(self):
        GeometricSource2D._onRequestInformation(self)
        bnds = self.getOption('bounds')
        self._vtksource.SetBounds(bnds[0], bnds[1], bnds[2], bnds[3], 0, 0)

    def getBounds(self):
        bnds = self._vtksource.GetBounds()
        return (bnds[0], bnds[1], bnds[2], bnds[3])
