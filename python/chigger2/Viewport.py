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
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import mooseutils
from . import utils
from . import base


class Viewport(utils.KeyBindingMixin, base.ChiggerAlgorithm):
    """
    The ChiggerResult is the base class for creating renderered objects. This class
    contains a single vtkRenderer to which many actors can be added.
    """

    # The type of input (as a string), see VTKPythonAlgoritimBase
    VTKINPUTTYPE = None

    @classmethod
    def validParams(cls):
        opt = base.ChiggerAlgorithm.validParams()
        opt += utils.KeyBindingMixin.validParams()

        opt.add('light', vtype=float,
                doc="Intensity of a 'headlight' to add to the renderer.")
        opt.add('layer', default=0, vtype=int,
                doc="The VTK layer within the render window.")
        opt.add('xlim', (0, 1), vtype=float, size=2,
                doc="The minimum and maximum viewport coordinates in the x-direction.")
        opt.add('ylim', (0, 1), vtype=float, size=2,
                doc="The minimum and maximum viewport coordinates in the y-direction.")
        opt.add('camera', None, vtype=vtk.vtkCamera,
                doc="The VTK camera to utilize for viewing the results.")
        opt.add('background', (0.0, 0.0, 0.0), vtype=float, size=3,
                doc="The primary background color.")
        opt.add('background2', None, vtype=float, size=3,
                doc="The secondary background color, when supplied this creates a gradient " \
                    "background")
        return opt

    @staticmethod
    def validKeyBindings():

        bindings = utils.KeyBindingMixin.validKeyBindings()
        bindings.add('c', Viewport.printCamera,
                     desc="Display the camera settings for this object.")
        bindings.add('o', Viewport.printParams,
                     desc="Display the available key, value options for this result.")
        bindings.add('o', Viewport.printSetParams, shift=True,
                     desc="Display the available key, value options as a 'setParams' method call.")

        bindings.add('right', Viewport._setViewport, args=(0, 0.025),
                     desc="Increase the viewport x-min value.")
        bindings.add('left', Viewport._setViewport, args=(0, -0.025),
                     desc="Increase the viewport x-min value.")

        bindings.add('right', Viewport._setViewport, args=(2, 0.025), shift=True,
                     desc="Decrease the viewport x-max value.")
        bindings.add('left', Viewport._setViewport, args=(2, -0.025), shift=True,
                     desc="Decrease the viewport x-max value")

        bindings.add('up', Viewport._setViewport, args=(1, 0.025),
                     desc="Increase the viewport y-min value.")
        bindings.add('down', Viewport._setViewport, args=(1, -0.025),
                     desc="Increase the viewport y-min value.")

        bindings.add('up', Viewport._setViewport, args=(3, 0.025), shift=True,
                     desc="Decrease the viewport y-max value.")
        bindings.add('down', Viewport._setViewport, args=(3, -0.025), shift=True,
                     desc="Decrease the viewport y-max value")

        return bindings

    def __init__(self, window, **kwargs):
        utils.KeyBindingMixin.__init__(self)
        base.ChiggerAlgorithm.__init__(self, nInputPorts=0, nOutputPorts=0, **kwargs)

        # Create renderer the viewport
        self._vtkrenderer = vtk.vtkRenderer()

        # List of ChiggerSource objects
        self.__sources = list()

        # Add to the Window
        window.add(self)

    def getVTKRenderer(self):
        """
        Return the vtk.vtkRenderer object
        """
        return self._vtkrenderer

    def sources(self):
        """
        Return the list of ChiggerSource objects
        """
        return self.__sources

    def add(self, arg):
        """
        Append the source object(s) to the renderer.
        """

        # "composite" source contain more than one VTKActor
        if isinstance(arg, base.ChiggerCompositeSource):
            for actor in arg.getVTKActors():
                self._vtkrenderer.AddActor(actor)

        # all other sources contain a single actor
        else:
            actor = arg.getVTKActor()
            if actor is not None:
                self._vtkrenderer.AddActor(actor)

        self.__sources.append(arg)

    def remove(self, arg):
        """
        Remove the source objects(s)
        """
        if arg in self.__sources:
            self.__sources.remove(arg)

            if isinstance(arg, base.ChiggerCompositeSource):
                for actor in arg.getVTKActors():
                    self._vtkrenderer.RemoveActor(actor)
            elif arg.getVTKActor() is not None:
                self._vtkrenderer.RemoveActor(arg.getVTKActor())
        else:
            msg = "The supplied source object '{}' is not owned by this viewport."
            self.warning(msg, arg.name())

    def updateInformation(self):
        """
        Update the sources if the Viewport updates

        The Viewport is a ChiggerAlgorithm, but doesn't have inputs or outputs. It is just using
        the VTK logic to update itself and the associated source objects. This is likely a bit of
        an abuse of the VTK design, but it works well and keeps the design consistent.
        """
        base.ChiggerAlgorithm.updateInformation(self)
        for source in self.__sources:
            source.updateInformation()

    def updateData(self):
        """
        Update the sources if the Viewport updates

        See updateInformation
        """
        base.ChiggerAlgorithm.updateData(self)
        for source in self.__sources:
            source.updateData()

    def _onRequestInformation(self, inInfo, outInfo):
        """
        Update Viewport settings for supplied parameters.
        """
        base.ChiggerAlgorithm._onRequestInformation(self, inInfo, outInfo)

        # Viewport size/location
        x = self.getParam('xlim')
        y = self.getParam('ylim')
        self._vtkrenderer.SetViewport(x[0], y[0], x[1], y[1])

        # Layer
        if self.isParamValid('layer'):
            layer = self.getParam('layer')
            if layer < 0:
                self.error("The 'layer' option must be zero or greater but {} provided.", layer)
            self._vtkrenderer.SetLayer(layer)

        # Background
        self.assignParam('background', self._vtkrenderer.SetBackground)
        self.assignParam('background2', self._vtkrenderer.SetBackground2)
        self._vtkrenderer.SetGradientBackground(self.isParamValid('background2'))

        # Camera
        self.assignParam('camera', self._vtkrenderer.SetActiveCamera)

        #self._vtkrenderer.ResetCameraClippingRange()


    def printCamera(self, *args): #pylint: disable=unused-argument
        """Keybinding callback."""
        print('\n'.join(utils.print_camera(self._vtkrenderer.GetActiveCamera())))

    def increaseXmin(self, *args):
        self._setViewport(0, 0.05)

    def decreaseXmin(self, *args):
        self._setViewport(0, -0.05)

    def increaseXmax(self, *args):
        self._setViewport(2, 0.05)

    def decreaseXmax(self, *args):
        self._setViewport(2, -0.05)

    def _setViewport(self, index, increment):
        x_min, y_min, x_max, y_max = self.getParam('viewport')
        c = list(self.getParam('viewport'))
        c[index] += increment

        x_min = round(c[0], 3) if (c[0] >= 0 and c[0] < c[2]) else x_min
        x_max = round(c[2], 3) if (c[2] <= 1 and c[0] < c[2]) else x_max

        y_min = round(c[1], 3) if (c[1] >= 0 and c[1] < c[3]) else y_min
        y_max = round(c[3], 3) if (c[3] <= 1 and c[1] < c[3]) else y_max

        self.setParams(viewport=(x_min, y_min, x_max, y_max))
        self.updateInformation()
        self.printParam('viewport')
