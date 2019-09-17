import vtk
import numpy as np
import math
from .. import base, utils, filters
from GeometricSource import GeometricSource2D

class Rectangle(GeometricSource2D):
    VTKSOURCETYPE = vtk.vtkPlaneSource
    PRECISION = 5

    @staticmethod
    def validOptions():
        opt = GeometricSource2D.validOptions()
        opt += utils.ActorOptions.validOptions()
        opt += base.ColorMap.validOptions()

        opt.add("bounds", None, vtype=float, size=4,
                doc="The bounding box for the cube [xmin, xmax, ymin, ymax].")

        # TODO: Do I need the ability to make diamonds and stuff???
        #opt.add('origin', default=(0, 0, 0), vtype=float, size=3,
        #        doc='Define the origin of the plane.')
        #opt.add('point1', default=(1, 0, 0), vtype=float, size=3,
        #        doc='Define the first edge of the plane (origin->point1).')
        #opt.add('point2', default=(0, 1, 0), vtype=float, size=3,
        #        doc='Define the second edge of the plane (origin->point2).')
        opt.add('resolution', default=(1, 1), vtype=int, size=2,
                doc="Define the number of subdivisions in the x- and y-direction of the plane.")

        opt.add('rotate', 0, vtype=int, doc="Angle of rotation in degrees, rotate about the center of the rectangle.")

        opt.add('point_data', None, vtype=vtk.vtkFloatArray,
                doc="The VTK point data to attach to the vtkMapper for this object")

        opt.add('coordinate_system', 'normalized_viewport', vtype=str,
                allow=('normalized_viewport', 'viewport'), doc="Set the input coordinate system.")

        return opt

    def __init__(self, *args, **kwargs):
        GeometricSource2D.__init__(self, *args, **kwargs)
        self._colormap = base.ColorMap()

    def getBounds(self):
        bnds = self.getOption('bounds')
        return (bnds[0], bnds[1], bnds[2], bnds[3])

    def applyOptions(self):
        """
        Set the options for this cube. (public)
        """
        GeometricSource2D.applyOptions(self)

        if self._vtkmapper.GetTransformCoordinate() is None:
            self._vtkmapper.SetTransformCoordinate(vtk.vtkCoordinate())
        coordinate = self._vtkmapper.GetTransformCoordinate()
        if self.getOption('coordinate_system') == 'normalized_viewport':
            coordinate.SetCoordinateSystemToNormalizedViewport()
        else:
            coordinate.SetCoordinateSystemToViewport()

        bnds = self.getOption('bounds')
        p0 = (bnds[0], bnds[2], 0)
        p1 = (bnds[0], bnds[3], 0)
        p2 = (bnds[1], bnds[2], 0)

        angle = self.getOption('rotate')
        if angle > 0:
            center = ((p1[0] + p2[0])/2., (p1[1] + p2[1])/2.)
            p0 = utils.rotate_point(p0, center, angle)
            p1 = utils.rotate_point(p1, center, angle)
            p2 = utils.rotate_point(p2, center, angle)

        self._vtksource.SetOrigin(p0)
        self._vtksource.SetPoint1(p1)
        self._vtksource.SetPoint2(p2)

        if self.isOptionValid('resolution'):
            self._vtksource.SetResolution(*self.getOption('resolution'))

        pdata = self.getOption('point_data')
        if pdata is not None:
            self._vtksource.Update()
            self._vtksource.GetOutput().GetPointData().SetScalars(pdata)
            self._vtkmapper.SetScalarRange(pdata.GetRange())

        self._colormap.setOptions(**self._options.toDict('cmap', 'cmap_reverse',
                                                         'cmap_num_colors', 'cmap_range'))
        if self.isOptionValid('cmap'):
            self._vtkmapper.SetLookupTable(self._colormap())
            self._vtkmapper.SetUseLookupTableScalarRange(True)

    def zoom(self, factor):
        bnds = self.getOption('bounds')
        bnds = (round(bnds[0] + factor, self.PRECISION),
                round(bnds[1] - factor, self.PRECISION),
                round(bnds[2] + factor, self.PRECISION),
                round(bnds[3] - factor, self.PRECISION))
        self.setOptions(bounds=bnds)
        self.printOption('bounds')

    def move(self, dx, dy):
        if self.getOption('coordinate_system') == 'normalized_viewport':
            sz = self._viewport.getVTKRenderer().GetSize()
            dx = dx/float(sz[0])
            dy = dy/float(sz[1])

        bnds = self.getOption('bounds')
        bnds = (round(bnds[0] + dx, self.PRECISION),
                round(bnds[1] + dx, self.PRECISION),
                round(bnds[2] + dy, self.PRECISION),
                round(bnds[3] + dy, self.PRECISION))
        self.setOptions(bounds=bnds)
        self.printOption('bounds')
