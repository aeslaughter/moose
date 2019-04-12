import logging
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import base



#TODO: Set number of input/output ports and associated types
#TODO: Create a GeometricResult that is setup to accept these object: mapper=vtkPolyDataMapper, actor=vtkActor

class GeometricSourceBase(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):
    """Base class for geometric objects that are passed into ChiggerResult objects."""

    #: The underlying VTK type, this should be set by the child class.
    VTKSOURCETYPE = None

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()
        #opt.add('required', default=False, vtype=bool,
        #        doc="When set to True this filter will be created automatically.")
        return opt

    def __init__(self, **kwargs):
        self._vtksource = self.VTKSOURCETYPE()

        base.ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self)


    def RequestData(self, request, inInfo, outInfo):
        self.log('RequestData', level=logging.DEBUG)

        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())

        #self._vtkfilter.SetInputData(inp)
        self._vtksource.Update()
        opt.ShallowCopy(self._vtksource.GetOutput())
        return 1

    def applyOptions(self):
        base.ChiggerAlgorithm.applyOptions(self)
