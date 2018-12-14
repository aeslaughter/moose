import vtk
import logging
from ChiggerObject import ChiggerObject
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase



class ChiggerAlgorithm(ChiggerObject):#, VTKPythonAlgorithmBase):
    """
    A ChiggerObject that also handles setting the VTK modified status as options change.
    """

    #@staticmethod
    #def nInputPorts(num):
    #    def create(cls):
    #        cls.__nInputPorts__ = num
    #        return cls
    #    return create

    #@staticmethod
    #def nOutputPorts(num):
    #    def create(cls):
    #        cls.__nInputPorts__ = num
    #        return cls
    #    return create


    #__nOutputPorts__ = 0
    #__nInputPorts__ = 0
    #__inputType__ = ''
    #__outputType__ = ''



    #OptionsModifiedEvent = vtk.vtkCommand.UserEvent + 1

    def __init__(self, **kwargs):

        if not isinstance(self, VTKPythonAlgorithmBase):
            msg = "ChiggerAlgorithm based objects must also inherit from VTKPythonAlgorithmBase."
            LOG.exception(msg)


        #VTKPythonAlgorithmBase.__init__(self,
        #                                nInputPorts=kwargs.pop('nInputPorts', 0),#self.__nInputPorts__,
        #                                inputType=kwargs.pop('inputType', None), #self.__inputType__,
        #                                nOutputPorts=kwargs.pop('nOutputPorts', 0), #self.__nOutputPorts__,
        #                                outputType=kwargs.pop('outputType', None))#self.__outputType__)
        ChiggerObject.__init__(self, **kwargs)

        # Create an observer that triggers
        #self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.applyOptions)

        # Set the VTK modified time, this is needed to make sure the options for this class
        # are all older than the class itself.
        self.Modified()

    def setOptions(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        print type(self), args, kwargs
        ChiggerObject.setOptions(self, *args, **kwargs)
        if self._options.modified() > self.GetMTime():
            self.log('applyOptions()', level=logging.DEBUG)
            self.applyOptions()
            #self.log('Modified()', level=logging.DEBUG)
            self.Modified()

    def applyOptions(self):
        pass
