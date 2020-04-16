import vtk
import logging
from .ChiggerObject import ChiggerObjectBase
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class ChiggerAlgorithm(ChiggerObjectBase, VTKPythonAlgorithmBase):
    """
    A base class for objects that require options and are a part of the VTK pipeline.

    The vtkPythonAlgorithm is designed to create custom python tools for plugging into to the VTK
    pipeline.
        https://blog.kitware.com/vtkpythonalgorithm-is-great
        https://blog.kitware.com/a-vtk-pipeline-primer-part-1

    This object leverages this design and adds an interface layer designed for chigger. The main
    purpose is to shield the interaction with VTK objects as much as possible and most importantly
    automatically invoke the proper calls when parameters are modified.

    It also adds a new layer to the normal VTK callbacks that calls Modified if a parameter
    changes. This is also used to check for file updates in the ExodusReader.
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

    def updateObject(self):
        """
        This is the one call that should be made to update the object.
        """
        self._onRequestModified()
        self.UpdateInformation()
        self.Update()

    def _onRequestModified(self):
        """
        This method is designed to be overridden, but be sure to call the base version to maintain
        correct behavior.

        The purpose of this method is to call the VTK method self.Modified(), which indicates to the
        VTK pipeline that something has changed an the class needs to be updated. The ExodusReader
        class uses this to check if the files associated with the reader have changed.
        """
        self.debug('_onRequestModified')
        if self._input_parameters.modified() > self.GetMTime():
            self.debug('_onRequestModified::Modified')
            self.Modified()

    def _onRequestInformation(self):
        """
        This is called by the VTK self.UpdateInformation function, if needed.

        https://vtk.org/Wiki/VTK/Tutorials/New_Pipeline
            > The rule here is to provide or compute as much information as you can without actually
            > executing (or reading in the entire data file) and without taking up significant CPU
            > time.
        """
        self.debug('_onRequestInformation')

    def _onRequestData(self, inInfo, outInfo):
        """
        This is called by the VTK self.UpdateInformation function, if needed.

        https://vtk.org/Wiki/VTK/Tutorials/New_Pipeline
            > Finally REQUEST_DATA will be called and the algorithm should fill in the output ports
            > data objects.
        """
        self.debug('_onRequestData')

    def RequestInformation(self, request, inInfo, outInfo):
        """
        Actual function called by VTK as required by VTKPythonAlgorithmBase, chigger objects
        should override _onRequestInformation.
        """
        self.debug('RequestInformation')
        retcode = self._onRequestInformation()
        if retcode is None:
            retcode = 1
        return retcode

    def RequestData(self, request, inInfo, outInfo):
        """
        Actual function called by VTK as required by VTKPythonAlgorithmBase, chigger objects
        should override _onRequestData.
        """
        self.debug('RequestData')
        retcode = self._onRequestData(inInfo, outInfo)
        if retcode is None:
            retcode = 1
        return retcode
