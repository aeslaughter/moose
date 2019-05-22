import vtk
import numpy as np
import math
from .. import base, utils, misc, filters
from GeometricSourceBase import GeometricSourceBase

class Rectangle(GeometricSourceBase):
    VTKACTORTYPE = vtk.vtkActor2D
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D
    VTKSOURCETYPE = vtk.vtkPlaneSource

    @staticmethod
    def validOptions():
        opt = GeometricSourceBase.validOptions()
        opt += utils.ActorOptions.validOptions()
        opt += misc.ColorMap.validOptions()
        opt.add('origin', default=(0, 0, 0), vtype=float, size=3,
                doc='Define the origin of the plane.')
        opt.add('point1', default=(1, 0, 0), vtype=float, size=3,
                doc='Define the first edge of the plane (origin->point1).')
        opt.add('point2', default=(0, 1, 0), vtype=float, size=3,
                doc='Define the second edge of the plane (origin->point2).')
        opt.add('resolution', default=(1, 1), vtype=int, size=2,
                doc="Define the number of subdivisions in the x- and y-direction of the plane.")

        opt.add('rotate', 0, vtype=int, doc="Angle of rotation in degrees.")

        opt.add('point_data', None, vtype=vtk.vtkFloatArray,
                doc="The VTK point data to attach to the vtkMapper for this object")

        return opt

    def __init__(self, *args, **kwargs):

        self._colormap = misc.ColorMap()

        GeometricSourceBase.__init__(self, *args, **kwargs)

        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToNormalizedViewport()
        self._vtkmapper.SetTransformCoordinate(coordinate)


    def applyOptions(self):
        """
        Set the options for this cube. (public)
        """
        GeometricSourceBase.applyOptions(self)

        angle = self.getOption('rotate')
        if angle > 0:
            p0 = self.getOption('origin')
            p1 = self.getOption('point1')
            p2 = self.getOption('point2')

            self.assignOption('origin', self._vtksource.SetOrigin)
            self._vtksource.SetPoint1(utils.rotate_point(p1, p0, angle))
            self._vtksource.SetPoint2(utils.rotate_point(p2, p0, angle))

        else:
            self.assignOption('origin', self._vtksource.SetOrigin)
            self.assignOption('point1', self._vtksource.SetPoint1)
            self.assignOption('point2', self._vtksource.SetPoint2)

        if self.isOptionValid('resolution'):
            self._vtksource.SetResolution(*self.getOption('resolution'))

        pdata = self.getOption('point_data')
        if pdata is not None:
            self._vtksource.Update()
            self._vtksource.GetOutput().GetPointData().SetScalars(pdata)
            self._vtkmapper.SetScalarRange(pdata.GetRange())

        self._colormap.setOptions(**self._options.toDict('cmap'))
        if self.isOptionValid('cmap'):
            self._vtkmapper.SetLookupTable(self._colormap())
