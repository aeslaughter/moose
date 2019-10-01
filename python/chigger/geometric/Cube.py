#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import vtk
from .GeometricSource import GeometricSource

class Cube(GeometricSource):
    """
    Single Cube object.
    """
    VTKSOURCETYPE = vtk.vtkCubeSource

    @staticmethod
    def validOptions():
        opt = GeometricSource.validOptions()
        opt.add("bounds", None, vtype=float, size=6,
                doc="The bounding box for the cube [xmin, xmax, ymin, ymax, zmin, zmax]. This " \
                "will overwrite the 'lengths' and 'center' options.")
        opt.add('lengths', None, vtype=float, size=3,
                doc="The lengths of the cube in the x,y,z-directions.")
        opt.add('center', None, vtype=float, size=3, doc="The center of the box.")
        return opt

    def _onUpdateInformation(self):
        """
        Set the options for this cube. (public)
        """
        GeometricSource._onUpdateInformation(self)

        if self.isOptionValid('center'):
            self._vtksource.SetCenter(self.getOption('center'))

        if self.isOptionValid('lengths'):
            x, y, z = self.getOption('lengths')
            self._vtksource.SetXLength(x)
            self._vtksource.SetYLength(y)
            self._vtksource.SetZLength(z)

        if self.isOptionValid('bounds'):
            self._vtksource.SetBounds(*self.getOption('bounds'))
