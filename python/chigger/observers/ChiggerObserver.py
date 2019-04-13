#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import logging
import weakref
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from .. import base

class ChiggerObserver(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):
    """
    Base class for defining VTK observer functions.

    This object is a base class and not intended for general use, see TimerObserver as an example.
    """
    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()
        return opt

    def __init__(self, window, **kwargs):
        self._window = weakref.ref(window)

        #VTKPythonAlgorithmBase.__init__(self)
        #base.ChiggerAlgorithm.__init__(self, **kwargs)

        #self.SetNumberOfInputPorts(1)
        #self.SetNumberOfOutputPorts(0)
        #self.InputType = 'vtkPythonAlgorithm'
        #self.SetInputConnection(window.GetOutputPort(0))


    #def RequestData(self, request, inInfo, outInfo):

        #inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        #self.SetInputData(inp)
    #    return 1
    #def init(self, window):
    #    """
    #    Initialize the observer, this is called by the RenderWindow automatically.

    #    NOTE: This is an internal method, do not call it.
    #    """
    #    self._window = window

    def terminate(self):
        """
        Terminate the render window.
        """
        #self._window.getVTKInteractor().TerminateApp()

    #def __del__(self):
    #    self.log('__del__()', level=logging.DEBUG)
    #    self._window = None
