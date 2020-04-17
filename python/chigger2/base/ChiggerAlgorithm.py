import vtk
import logging
from .ChiggerObject import ChiggerObject
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class ChiggerAlgorithm(ChiggerObject, VTKPythonAlgorithmBase):
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
    changes. This is also used to check for file updates in the ExodusReader. See the documentation
    in self.updateModified for further information.

    TODO: There is probably a method for adding new requests via VTK so that the UpdateInformation
          and Update methods could do the updateModified call, but figuring that out was beyond my
          knowledge and the time sink is already deep.
    """

    def __init__(self, nInputPorts=0, nOutputPorts=0, outputType=None, inputType=None, **kwargs):
        ChiggerObject.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self)

        self.SetNumberOfInputPorts(nInputPorts)
        self.SetNumberOfOutputPorts(nOutputPorts)
        if outputType is not None:
            self.OutputType = outputType
        if inputType is not None:
            self.InputType = inputType

        # Set the VTK modified time, this is needed to make sure the options for this class are all
        # older than the class itself.
        self.objectModified()

    def objectModified(self):
        """
        Indicate that the object has been modified. This informs VTK that thinks need to be
        re-rendered. This generally should only be called from within _onRequestModified.

        This mainly exists to make the API consistent and for testing the callbacks.
        """
        self.debug('objectModified')
        self.Modified()

    def updateObject(self):
        """
        Call all necessary functions to ensure the information and data of the object are updated.
        """
        self.debug('updateObject')
        self.updateModified()
        self.updateInformation()
        self.updateData()

    def updateModified(self):
        """
        Determine if the object has been modified and requires update within VTK.

        This is a chigger add-on function to supplement the VTK UpdateInformation/Update pipeline.
        This was added to support the ExodusReader filename detection. The VTK methods
        UpdateInformation and Update will call RequestInformation and RequestData respectively, but
        only if Modified() was called. That is calling UpdateInformation twice in a row will only
        result in a single call to RequestInformation.

        To support the automatic checking of file changes in the ExodusReader a function needs to
        exist that can be called again an again: updateModified. This will call the 'protected'
        _onRequestModified every time, see the help _onRequestModified for more information.
        """
        self.debug('updateModified')
        retcode = self._onRequestModified()

        # Mimic return code behavior of VTK UpdateInformation and Update methods
        if retcode is None:
            retcode = 1
        if retcode != 1:
            msg = 'Failed request callback, _onRequestModified returned an invalid code of {}.'
            self.error(msg, retcode)

    def updateInformation(self):
        """
        Alias for VTK UpdateInformation method to provide for a uniform API.
        """
        self.debug('updateInformation')
        self.UpdateInformation()

    def updateData(self):
        """
        Alias for VTK Update method to provide for a uniform API.
        """
        self.debug('updateData')
        self.Update()

    def setParam(self, *args, **kwargs):
        """
        Override ChiggerObject.setParam to call updateModified
        """
        ChiggerObject.setParam(self, *args, **kwargs)
        self.__paramModifiedHelper()

    def setParams(self, *args, **kwargs):
        """
        Override ChiggerObject.setParams to call updateModified
        """
        ChiggerObject.setParams(self, *args, **kwargs)
        self.__paramModifiedHelper()

    def _onRequestModified(self):
        """
        This method is designed to be overridden, but be sure to call the base version to maintain
        correct behavior.

        The purpose of this method is to call the VTK method self.Modified(), which indicates to the
        VTK pipeline that something has changed an the class needs to be updated. The ExodusReader
        class uses this to check if the files associated with the reader have changed.
        """
        self.debug('_onRequestModified')
        self.__paramModifiedHelper()
        return 1

    def _onRequestInformation(self, inInfo, outInfo):
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

    def __paramModifiedHelper(self):
        """
        Helper to mark the object as modified if the parameters change.
        """
        if self._input_parameters.modified() > self.GetMTime():
            self.objectModified()

    def RequestInformation(self, request, inInfo, outInfo):
        """
        Actual function called by VTK as required by VTKPythonAlgorithmBase, chigger objects
        should override _onRequestInformation.
        """
        self.debug('RequestInformation')
        retcode = self._onRequestInformation(inInfo, outInfo)
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
