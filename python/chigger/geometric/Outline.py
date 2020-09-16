import math
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

    def _getBounds(self):
        return self._vtksource.GetBounds()

    def _onRequestInformation(self, *args):
        GeometricSource._onRequestInformation(self, *args)
        self._vtksource.SetBounds(bnds[0], bnds[1], bnds[2], bnds[3], bnds[4], bnds[5])


class Outline2D(GeometricSource2D):
    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSource2D.validOptions()
        opt.add('bounds', None, vtype=float, size=4,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax].")
        opt.add("offset", 0, vtype=float,
                doc="The amount, in viewport coordinates, to offset the bounding box")
        return opt

    def _onRequestInformation(self, *args):
        GeometricSource2D._onRequestInformation(self, *args)
        self._vtksource.SetBounds(*self._getBounds())

    def _getBounds(self):
        bnds = list(self.getOption('bounds'))
        offset = self.getOption('offset')
        for i in [0, 2]:
            if (bnds[i] - offset) >= 0:
                bnds[i] = bnds[i] - offset
            else:
                self.error("The bounds[{}] value ({}) is less than zero with offset applied.", i, bnds[i])
        for i in [1, 3]:
            if (bnds[i] + offset) <= 1:
                bnds[i] = bnds[i] + offset
            else:
                self.error("The bounds[{}] value ({}) is greater than one with offset applied.", i, bnds[i])

        return (bnds[0], bnds[1], bnds[2], bnds[3], 0, 0)
