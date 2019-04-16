import vtk
from GeometricSourceBase import GeometricSourceBase

class OutlineSource(GeometricSourceBase):

    VTKSOURCETYPE = vtk.vtkOutlineSource

    @staticmethod
    def validOptions():
        opt = GeometricSourceBase.validOptions()
        opt.add('bounds', None, vtype=float, size=6,
                doc="The bounding box of the object to outline: [xmin, xmax, ymin, ymax, zmin, zmax].")
        opt.add('width', 1, vtype=float, doc="The line width for the outline.")
        return opt

    def applyOptions(self):
        GeometricSourceBase.applyOptions(self)
        if self.isOptionValid('bounds'):
            self._vtksource.SetBounds(self.getOption('bounds'))
