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
    def validOptions(cls):
        opt = base.ChiggerAlgorithm.validOptions()
        opt += utils.KeyBindingMixin.validOptions()

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

        # Initialize class members
        self.__sources = list()
        self._vtkrenderer = vtk.vtkRenderer()

        # Verify renderer type
        if not isinstance(self._vtkrenderer, vtk.vtkRenderer):
            msg = "The supplied value for the renderer is a {} but it must be of type vtkRenderer."
            raise mooseutils.MooseException(msg.format(type(self._vtkrenderer).__name__))

        # Add the Viewport to the Window and store a reference without reference counting, the
        # underlying VTK objects keep track of things and without the weakref here there is a
        # circular reference between the vtkRenderer and vtkRenderWindow objects. The _window
        # property should be used by objects that need information from the Window object.
        window.add(self)
        #self.__window_weakref = None# weakref.ref(window)

        self._vtkrenderer.InteractiveOff()


    #def _window(self):
    #    """Property so that self._w#indow acts like the actual window object."""
    #    return self.__window_weakref()

    def add(self, arg):

        if isinstance(arg, base.ChiggerCompositeSource):
            for actor in arg.getVTKActors():
                self._vtkrenderer.AddActor(actor)

        else:
            actor = arg.getVTKActor()
            if actor is not None:
                self._vtkrenderer.AddActor(actor)

        self.__sources.append(arg)

    def remove(self, arg):
        if arg in self.__sources:
            self.__sources.remove(arg)

            if isinstance(arg, base.ChiggerCompositeSource):
                for actor in arg.getVTKActors():
                    self._vtkrenderer.RemoveActor(actor)
            elif arg.getVTKActor() is not None:
                self._vtkrenderer.RemoveActor(arg.getVTKActor())


    #def RequestData(self, request, inInfo, outInfo):
    #    base.ChiggerAlgorithm.RequestData(self, request, inInfo, outInfo)
    #    opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
    #    print opt
    #    return 1

    def updateInformation(self):
        base.ChiggerAlgorithm.updateInformation(self)
        for source in self.__sources:
            source.updateInformation()

    def updateData(self):
        base.ChiggerAlgorithm.updateData(self)
        for source in self.__sources:
            source.updateData()


    def _onRequestInformation(self):
        base.ChiggerAlgorithm._onRequestInformation(self)
        self._vtkrenderer.SetViewport(self.getOption('viewport'))

        if self.isOptionValid('layer'):
            layer = self.getOption('layer')
            if layer < 0:
                self.error("The 'layer' option must be zero or greater but {} provided.", layer)
            self._vtkrenderer.SetLayer(layer)

        self._vtkrenderer.SetBackground(self.getOption('background'))
        if self.isOptionValid('background2'):
            self._vtkrenderer.SetBackground2(self.getOption('background2'))
            self._vtkrenderer.SetGradientBackground(True)
        else:
            self._vtkrenderer.SetGradientBackground(False)

        #self._vtkrenderer.ResetCameraClippingRange()
        self._vtkrenderer.ResetCamera()

    def getVTKRenderer(self):
        """Return the vtk.vtkRenderer object."""
        return self._vtkrenderer

    def sources(self):
        return self.__sources

    def getSource(self, index=-1):
        return self.__sources[index]

   # def getBounds(self):
   #     bnds = self.getOption('viewport')
   #     return (bnds[0], bnds[2], bnds[1], bnds[3])

    def __len__(self):
        """
        The number of source objects.
        """
        return len(self.__sources)

    def __iter__(self):
        for source in self.__sources:
            yield source

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
        x_min, y_min, x_max, y_max = self.getOption('viewport')
        c = list(self.getOption('viewport'))
        c[index] += increment

        x_min = round(c[0], 3) if (c[0] >= 0 and c[0] < c[2]) else x_min
        x_max = round(c[2], 3) if (c[2] <= 1 and c[0] < c[2]) else x_max

        y_min = round(c[1], 3) if (c[1] >= 0 and c[1] < c[3]) else y_min
        y_max = round(c[3], 3) if (c[3] <= 1 and c[1] < c[3]) else y_max

        self.setOptions(viewport=(x_min, y_min, x_max, y_max))
        self.printOption('viewport')
