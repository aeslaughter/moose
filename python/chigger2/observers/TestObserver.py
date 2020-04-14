#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import sys
import io
import vtk
from .SingleShotObserver import SingleShotObserver


class TestObserverException(Exception):
    def __init__(self, text, *args, **kwargs):
        Exception.__init__(self, text.format(*args, **kwargs))

class TestObserver(SingleShotObserver):
    """
    Tool for simulating key strokes and mouse movements.
    """

    @staticmethod
    def validParams():
        params = SingleShotObserver.validParams()
        return params

    def __init__(self, *args, **kwargs):
        SingleShotObserver.__init__(self, *args, **kwargs)

    def keyPress(self, key, shift=False):
        """
        Simulate a key press.

        Inputs:
            key[str]: The key symbol (e.g. "k").
            shift[bool]: Flag for holding the shift key.
        """
        vtkinteractor = self._window.getVTKInteractor()
        if key is not None:
            vtkinteractor.SetKeySym(key)
        vtkinteractor.SetShiftKey(shift)
        vtkinteractor.InvokeEvent(vtk.vtkCommand.KeyPressEvent, vtkinteractor)
        vtkinteractor.SetKeySym(None)
        vtkinteractor.SetShiftKey(False)

    def keyDown(self, key, shift=False):
        vtkinteractor = self._window.getVTKInteractor()
        vtkinteractor.SetKeySym(key)
        vtkinteractor.SetShiftKey(shift)
        vtkinteractor.InvokeEvent(vtk.vtkCommand.KeyPressEvent, vtkinteractor)

    def keyRelease(self):
        vtkinteractor = self._window.getVTKInteractor()
        vtkinteractor.SetKeySym(None)
        vtkinteractor.SetShiftKey(False)

    def mouseTranslate(self, x, y, shift=False):
        sz = self._window.getVTKWindow().GetSize()
        pos = [int(sz[0] * x), int(sz[1] * y)]

        vtkinteractor = self._window.getVTKInteractor()
        vtkinteractor = self._window.getVTKInteractor()
        if shift:
            vtkinteractor.SetShiftKey(True)
        vtkinteractor.SetTranslation(pos)
        vtkinteractor.InvokeEvent(vtk.vtkCommand.MouseMoveEvent, vtkinteractor)
        vtkinteractor.SetShiftKey(False)

    def mouseMove(self, x, y, shift=False): #pylint: disable=invalid-name
        """
        Simulate a mouse movement.

        Inputs:
            x[float]: Position relative to the current window size in the horizontal direction.
            y[float]: Position relative to the current window size in the vertical direction.
        """

        # Determine relative position
        sz = self._window.getVTKWindow().GetSize()
        pos = [int(sz[0] * x), int(sz[1] * y)]

        # Move the mouse
        vtkinteractor = self._window.getVTKInteractor()
        if shift:
            vtkinteractor.SetShiftKey(True)
        vtkinteractor.SetEventPosition(pos[0], pos[1])
        vtkinteractor.InvokeEvent(vtk.vtkCommand.MouseMoveEvent, vtkinteractor)
        vtkinteractor.SetShiftKey(False)

    def mouseWheelForward(self, count=1):
        vtkinteractor = self._window.getVTKInteractor()
        for i in range(count):
            vtkinteractor.InvokeEvent(vtk.vtkCommand.MouseWheelForwardEvent, vtkinteractor)

    def mouseWheelBackward(self, count=1):
        vtkinteractor = self._window.getVTKInteractor()
        for i in range(count):
            vtkinteractor.InvokeEvent(vtk.vtkCommand.MouseWheelBackwardEvent, vtkinteractor)

    def pressLeftMouseButton(self):
        """
        Simulate a left mouse click.
        """
        vtkinteractor = self._window.getVTKInteractor()
        vtkinteractor.InvokeEvent(vtk.vtkCommand.LeftButtonPressEvent, vtkinteractor)
