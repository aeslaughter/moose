import vtk
import logging
from ChiggerObject import ChiggerObject
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

LOG = logging.getLogger(__name__)


class ChiggerAlgorithm(ChiggerObject):
    """
    A ChiggerObject that also handles setting the VTK modified status as options change.
    """

    #OptionsModifiedEvent = vtk.vtkCommand.UserEvent + 1

    def __init__(self, **kwargs):
        ChiggerObject.__init__(self, **kwargs)

        #
        if not isinstance(self, VTKPythonAlgorithmBase):
            msg = "ChiggerAlgorithm based objects must also inherit from VTKPythonAlgorithmBase."
            LOG.exception(msg)

        # Set the VTK modified time, this is needed to make sure the options for this class
        # are all older than the class itself.
        self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.applyOptions)
        self.Modified()

    def setOptions(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        ChiggerObject.setOptions(self, *args, **kwargs)
        if self._options.modified() > self.GetMTime():
            self.Modified()

    def applyOptions(self, obj, event):
        print self.__class__.__name__, 'applyOptions', obj is self, event
