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
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import mooseutils
from . import utils
from . import base


class Viewport(utils.KeyBindingMixin, utils.ObserverMixin, base.ChiggerAlgorithm):
    """
    The ChiggerResult is the base class for creating renderered objects. This class
    contains a single vtkRenderer to which many actors can be added.
    """

    # The type of input (as a string), see VTKPythonAlgoritimBase
    VTKINPUTTYPE = None

    @classmethod
    def validOptions(cls):
        opt = base.ChiggerAlgorithm.validOptions()
        opt += utils.ObserverMixin.validOptions()

        opt.add('light', vtype=float,
               doc="Add a headlight with the given intensity to the renderer.")
        opt.add('layer', default=1, vtype=int,
                doc="The VTK layer within the render window.")
        opt.add('viewport', default=(0., 0., 1., 1.), vtype=float, size=4,
                doc="A list given the viewport coordinates [x_min, y_min, x_max, y_max], in " \
                    "relative position to the entire window (0 to 1).")
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
        bindings.add('o', Viewport.printOptions,
                     desc="Display the available key, value options for this result.")
        bindings.add('o', Viewport.printSetOptions, shift=True,
                     desc="Display the available key, value options as a 'setOptions' method call.")
        return bindings

    def __init__(self, *args, **kwargs):
        utils.KeyBindingMixin.__init__(self)
        utils.ObserverMixin.__init__(self)

        # Initialize class members
        self._sources = list()
        self._vtkrenderer = vtk.vtkRenderer()

        # Verify renderer type
        if not isinstance(self._vtkrenderer, vtk.vtkRenderer):
            msg = "The supplied value for the renderer is a {} but it must be of type vtkRenderer."
            raise mooseutils.MooseException(msg.format(type(self._vtkrenderer).__name__))

        # Setup VTKPythobnAlgorithmBase
        base.ChiggerAlgorithm.__init__(self, nInputPorts=len(args), inputType=self.VTKINPUTTYPE, **kwargs)

        for arg in args:
            self._add(arg)

        #


    def _add(self, arg):
        if arg.getVTKActor() is not None:
            self._vtkrenderer.AddActor(arg.getVTKActor())

        self._sources.append(arg)

    def _remove(self, arg):
        if arg in self._sources:
            self._sources.remove(arg)

            if arg.getVTKActor() is not None:
                self._vtkrenderer.RemoveActor(arg.getVTKActor())

    def applyOptions(self):
        base.ChiggerAlgorithm.applyOptions(self)
        self._vtkrenderer.SetViewport(self.getOption('viewport'))

        if self.isOptionValid('layer'):
            layer = self.getOption('layer')
            if layer < 0:
                self.log("The 'layer' option must be zero or greater but {} provided.", layer,
                         level=logging.ERROR)
            self._vtkrenderer.SetLayer(layer)

        self._vtkrenderer.SetBackground(self.getOption('background'))
        if self.isOptionValid('background2'):
            self._vtkrenderer.SetBackground2(self.getOption('background2'))
            self._vtkrenderer.SetGradientBackground(True)
        else:
            self._vtkrenderer.SetGradientBackground(False)


        self._vtkrenderer.ResetCameraClippingRange()

    def getVTKRenderer(self):
        """Return the vtk.vtkRenderer object."""
        return self._vtkrenderer

    def getSource(self, index=-1):
        return self._sources[index]

    def printCamera(self, *args): #pylint: disable=unused-argument
        """Keybinding callback."""
        print '\n'.join(utils.print_camera(self._vtkrenderer.GetActiveCamera()))

    def __len__(self):
        """
        The number of source objects.
        """
        return len(self._sources)

    def __iter__(self):
        for source in self._sources:
            yield source