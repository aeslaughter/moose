import vtk
import logging
from .ChiggerObject import ChiggerObjectBase
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class ChiggerAlgorithm(ChiggerObjectBase, VTKPythonAlgorithmBase):
    """
    A base class for objects that require options and are a part of the VTK pipeline.
    """

    def __init__(self, nInputPorts=0, nOutputPorts=0, outputType=None, inputType=None, **kwargs):
        ChiggerObjectBase.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self)

        self.SetNumberOfInputPorts(nInputPorts)
        self.SetNumberOfOutputPorts(nOutputPorts)
        if outputType is not None:
            self.OutputType = outputType
        if inputType is not None:
            self.InputType = inputType

        # Set the VTK modified time, this is needed to make sure the options for this class are all
        # older than the class itself.
        self.Modified()

    def updateInformation(self):
        self.debug('updateInformation')
        self.UpdateInformation()

    def updateData(self):
        self.debug('updateData')
        self.Update()

    def setParam(self, *args, **kwargs):
        ChiggerObjectBase.setParam(self, *args, **kwargs)
        if self._input_parameters.modified() > self.GetMTime():
            self.debug('setParam::Modified')
            self.Modified()

    def setParams(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        ChiggerObjectBase.setParams(self, *args, **kwargs)
        if self._input_parameters.modified() > self.GetMTime():
            self.debug('setParams::Modified')
            self.Modified()

    def _onRequestInformation(self):
        self.debug('_onRequestInformation')

    def _onRequestData(self, inInfo, outInfo):
        self.debug('_onRequestData')

    def RequestInformation(self, request, inInfo, outInfo):
        self.debug('RequestInformation')
        retcode = self._onRequestInformation()
        if retcode is None:
            retcode = 1
        return retcode

    def RequestData(self, request, inInfo, outInfo):
        self.debug('RequestData')
        retcode = self._onRequestData(inInfo, outInfo)
        if retcode is None:
            retcode = 1
        return retcode
