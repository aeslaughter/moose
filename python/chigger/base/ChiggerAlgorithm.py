import vtk
import logging
from ChiggerObject import ChiggerObjectBase
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import utils



class ChiggerAlgorithm(ChiggerObjectBase, VTKPythonAlgorithmBase):
    """
    A base class for objects that require options and are a part of the VTK pipeline.
    """

    def __init__(self, nInputPorts=0, nOutputPorts=0, outputType=None, inputType=None, **kwargs):

        VTKPythonAlgorithmBase.__init__(self)

        self.SetNumberOfInputPorts(nInputPorts)
        self.SetNumberOfOutputPorts(nOutputPorts)
        if outputType is not None:
            self.outputType = outputType
        if inputType is not None:
            self.inputType = inputType

        ChiggerObjectBase.__init__(self, **kwargs)

        # Set the VTK modified time, this is needed to make sure the options for this class
        # are all older than the class itself.
        self.Modified()

    def update(self, other):
        ChiggerObjectBase.update(self, other)
        if self._options.modified() > self.GetMTime():
            #self.applyOptions()
            self.Modified()

    def setOptions(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        ChiggerObjectBase.setOptions(self, *args, **kwargs)
        if self._options.modified() > self.GetMTime():
            #self.applyOptions()
            self.Modified()

    def applyOptions(self):
        self.log('applyOptions', level=logging.DEBUG)

    def RequestInformation(self, request, inInfo, outInfo):
        self.log('RequestInformation', level=logging.DEBUG)
        return 1

    def RequestData(self, request, inInfo, outInfo):
        self.log('RequestData', level=logging.DEBUG)
        self.applyOptions()
        return 1
