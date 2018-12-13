import vtk
from ChiggerFilter import ChiggerFilter

class GeometryFilter(ChiggerFilter):
    VTKFILTERTYPE = vtk.vtkCompositeDataGeometryFilter
