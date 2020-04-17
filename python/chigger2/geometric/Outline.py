import vtk
from .GeometricSource import GeometricSource, GeometricSource2D

class Outline(GeometricSource):

    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validParams():
        opt = GeometricSource.validParams()
        opt.add('bounds', None, vtype=float, size=6,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax, zmin, zmax].")
        return opt

    def _onRequestInformation(self, inInfo, outInfo):
        GeometricSource._onRequestInformation(self, inInfo, outInfo)
        self.assignParam('bounds', self._vtksource.SetBounds)


class Outline2D(GeometricSource2D):
    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validParams():
        opt = GeometricSource2D.validParams()
        opt.add('bounds', None, vtype=float, size=4,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax].")

        return opt

    def _onRequestInformation(self, inInfo, outInfo):
        GeometricSource2D._onRequestInformation(self, inInfo, outInfo)
        bnds = self.getParam('bounds')
        self._vtksource.SetBounds(bnds[0], bnds[1], bnds[2], bnds[3], 0, 0)

    def getBounds(self):
        bnds = self._vtksource.GetBounds()
        return (bnds[0], bnds[1], bnds[2], bnds[3])
