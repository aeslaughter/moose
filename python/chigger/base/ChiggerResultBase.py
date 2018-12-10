#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import collections
import textwrap
import vtk
import mooseutils

import chigger
from .. import utils
from ChiggerObject import ChiggerObject

class ChiggerResultBase(ChiggerObject, utils.KeyBindingMixin):
    """
    Base class for objects to be displayed with a single vtkRenderer object.

    Any object or set of objects that require a single vtkRenderer object should inherit from this
    and all settings for the vtkRender object should be placed in this class.

    If you are creating a new type of "result" object (i.e., something with a vtkRenderer) you will
    likely want to derive from one of the child classes of ChiggerResultBase, such as ChiggerResult.

    Inputs:
        see ChiggerObject
    """
    @staticmethod
    def validOptions():
        opt = ChiggerObject.validOptions()
        opt.add('interactive', default=True,
                doc="Control if the object may be selected with key bindings.")
        opt.add('light', vtype=float,
                doc="Add a headlight with the given intensity to the renderer.")
        opt.add('layer', default=1, vtype=int,
                doc="The VTK layer within the render window.")
        opt.add('viewport', default=(0., 0., 1., 1.), vtype=float, size=4,
                doc="A list given the viewport coordinates [x_min, y_min, x_max, y_max], in " \
                    "relative position to the entire window (0 to 1).")
        opt.add('camera', None, vtype=vtk.vtkCamera,
                doc="The VTK camera to utilize for viewing the results.")
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        bindings.add('c', ChiggerResultBase._printCamera,
                     desc="Display the camera settings for this object.")
        return bindings

    def __init__(self, renderer=None, **kwargs):
        super(ChiggerResultBase, self).__init__(**kwargs)
        self._vtkrenderer = renderer if renderer != None else vtk.vtkRenderer()
        self._vtklight = vtk.vtkLight()
        self._vtklight.SetLightTypeToHeadlight()
        self._vtkrenderer.SetInteractive(False)
        self._render_window = None

    def setRenderWindow(self, window):
        """
        Set the chigger.RenderWindow object (this should not be called).
        """
        self._render_window = window

    def getRenderWindow(self):
        """
        Return the chigger.RenderWindow object.
        """
        return self._render_window

    def getVTKRenderer(self):
        """
        Return the vtkRenderer object. (public)

        Generally, this should not be used. This method if mainly for the RenderWindow object to
        populate the list of renderers that it will be displaying.
        """
        return self._vtkrenderer

    def update(self, **kwargs):
        """
        Update the vtkRenderer settings. (override)

        Inputs:
            see ChiggerObject
        """
        super(ChiggerResultBase, self).update(**kwargs)

        # Render layer
        if self.isOptionValid('layer'):
            self._vtkrenderer.SetLayer(self.applyOption('layer'))

        # Viewport
        if self.isOptionValid('viewport'):
            self._vtkrenderer.SetViewport(self.applyOption('viewport'))

        # Camera
        if self.isOptionValid('camera'):
            self._vtkrenderer.SetActiveCamera(self.getOption('camera'))

        # Headlight
        if self.isOptionValid('light'):
            self._vtklight.SetIntensity(self.getOption('light'))
            self._vtkrenderer.AddLight(self._vtklight)

    def getBounds(self):
        """
        Return the bounding box of the results.

        By default this returns the bounding box of the viewport.
        """
        origin = self.getVTKRenderer().GetOrigin()
        size = self.getVTKRenderer().GetSize()
        return [origin[0], origin[0] + size[0], origin[1], origin[1] + size[1], 0, 0]

    def _printCamera(self, *args):
        print '\n'.join(utils.print_camera(self._vtkrenderer.GetActiveCamera()))
