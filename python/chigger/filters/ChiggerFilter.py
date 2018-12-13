import logging
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import base

class ChiggerFilter(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):
    """Base class for filter objects that are passed into ChiggerResult objects."""

    #: The underlying VTK type, this should be set by the child class.
    VTKFILTERTYPE = None

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()
        opt.add('required', default=False, vtype=bool,
                doc="When set to True this filter will be created automatically.")
        return opt

    def __init__(self, result, **kwargs):
        base.ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self)

        self._vtkfilter = self.VTKFILTERTYPE()
        self.__result = result

    def getChiggerResult(self):
        return self.__result


    #def getVTKFilter(self):
    #    return self._vtkfilter


    def RequestData(self, request, inInfo, outInfo):
        self.log('RequestData', level=logging.DEBUG)


        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())

        self._vtkfilter.SetInputData(inp)
        self._vtkfilter.Update()
        opt.ShallowCopy(self._vtkfilter.GetOutput())
        return 1

    def applyOptions(self):
        pass
