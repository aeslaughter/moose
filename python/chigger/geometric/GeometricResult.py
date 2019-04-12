
import vtk
from .. import base

class GeometricResult(base.ChiggerResult):

    INPUTTYPE = 'vtkPolyData'

    __FILTERS__ = list()
    __ACTIVE_FILTERS__ = set()

    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = base.ChiggerResult.validKeyBindings()
        return bindings

    #def __init__(self, *args, **kwargs):
    #    base.ChiggerResult.__init__(self, *args, **kwargs)

    #def applyOptions(self):
    #    base.ChiggerResult.applyOptions(self)
