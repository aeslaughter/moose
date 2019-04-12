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
        self._window = window

        VTKPythonAlgorithmBase.__init__(self)

        self.SetNumberOfInputPorts(0)
        self.SetNumberOfOutputPorts(0)

        base.ChiggerAlgorithm.__init__(self, **kwargs)

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
        self._window.getVTKInteractor().TerminateApp()

    #def __del__(self):
    #    self.log('__del__()', level=logging.DEBUG)
    #    self._window = None
