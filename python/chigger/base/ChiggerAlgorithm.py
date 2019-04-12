import vtk
import logging
from ChiggerObject import ChiggerObject
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import utils



class ChiggerAlgorithm(ChiggerObject):#, VTKPythonAlgorithmBase):
    """
    A ChiggerObject that also handles setting the VTK modified status as options change.
    """

    def __init__(self, **kwargs):

        if not isinstance(self, VTKPythonAlgorithmBase):
            msg = "ChiggerAlgorithm based objects must also inherit from VTKPythonAlgorithmBase."
            LOG.exception(msg)

        ChiggerObject.__init__(self, **kwargs)

        # Set the VTK modified time, this is needed to make sure the options for this class
        # are all older than the class itself.
        self.Modified()


    def setOptions(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        ChiggerObject.setOptions(self, *args, **kwargs)
        if self._options.modified() > self.GetMTime():
            self.log('applyOptions()', level=logging.DEBUG)
            self.applyOptions()
            self.Modified()

    def applyOptions(self):
        pass


class ChiggerAlgorithmSource(ChiggerAlgorithm):

    # The type of vtkProp to create (this should be defined in child class)
    VTKACTORTYPE = None

    # The type of vtkAbstractMapper to create (this should be defined in child class)
    VTKMAPPERTYPE = None


    @staticmethod
    def validOptions():
        opt = ChiggerAlgorithm.validOptions()
        opt += utils.ActorOptions.validOptions()
        return opt

    def __init__(self, *args, **kwargs):
        #self.__initialized = False

        # Create mapper
        self._vtkmapper = self.VTKMAPPERTYPE() if self.VTKMAPPERTYPE else None
        if (self._vtkmapper is not None) and not isinstance(self._vtkmapper, vtk.vtkAbstractMapper):
            msg = 'The supplied mapper is a {} but must be a vtk.vtkAbstractMapper type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkmapper).__name__))

        # Create the actor
        self._vtkactor = self.VTKACTORTYPE() if self.VTKACTORTYPE else None
        if (self._vtkactor is not None) and not isinstance(self._vtkactor, vtk.vtkProp):
            msg = 'The supplied actor is a {} but must be a vtk.vtkProp type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkactor).__name__))

        # Connect the mapper and actor and add the actor to the renderer
        if self._vtkmapper is not None:
            self._vtkactor.SetMapper(self._vtkmapper)

        ChiggerAlgorithm.__init__(self, *args, **kwargs)

    def getVTKActor(self):
        """
        Return the constructed vtk actor object. (public)

        Returns:
            An object derived from vtk.vtkProp.
        """
        return self._vtkactor

    def getVTKMapper(self):
        """
        Return the constructed vtk mapper object. (public)

        Returns:
            An object derived from vtk.vtkAbstractMapper
        """
        return self._vtkmapper

    #def init(self, vtkactor, vtkmapper):
    #    self.__initialized = True
    #    self._vtkactor = vtkactor
    #    self._vtkmapper = vtkmapper

    #def setOptions(self, *args, **kwargs):
    #    if self.__initialized:
    #        ChiggerAlgorithm.setOptions(self, *args, **kwargs)
    #    else:
    #        ChiggerObject.setOptions(self, *args, **kwargs)

    def applyOptions(self):
        ChiggerAlgorithm.applyOptions(self)
        utils.ActorOptions.applyOptions(self._vtkactor, self._options)

#def RequestInformation(self, *args):
#    return 1

#def RequestData(self, *args):
#    self.applyOptions()
#
