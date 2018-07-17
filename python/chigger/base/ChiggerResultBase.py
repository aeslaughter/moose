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
        opt.add('interactive', True, doc="Control if the object may be selected with key bindings.")
        opt.add('layer', 1, vtype=int, doc="The VTK layer within the render window.")
        opt.add('viewport', (0., 0., 1., 1.), vtype=float, size=4,
                doc="A list given the viewport coordinates [x_min, y_min, x_max, y_max], in " \
                    "relative position to the entire window (0 to 1).")
        opt.add('background', (0., 0., 0.), vtype=float, size=3,
                doc="The background color, only applied when the 'layer' option is zero. A " \
                    "background result is automatically added when chigger.RenderWindow is " \
                    "utilized.")
        opt.add('background2', None, vtype=float, size=3,
                doc="The second background color, when supplied this creates a gradient " \
                    "background, only applied when the 'layer' option is zero. A background " \
                    "result is automatically added when chigger.RenderWindow is utilized.")
        opt.add('gradient_background', False, doc="Enable/disable the use of a gradient background.")
        opt.add('camera', None, vtype=vtk.vtkCamera,
                doc="The VTK camera to utilize for viewing the results.")
        return opt

    def __init__(self, renderer=None, **kwargs):
        super(ChiggerResultBase, self).__init__(**kwargs)
        self._vtkrenderer = renderer if renderer != None else vtk.vtkRenderer()
        self._vtkrenderer.SetInteractive(False)
        self.addKeyBinding('c', self._printCamera, desc="Display the camera settings for this object.")

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
        #ResultEventHandler.update(self)


        # Render layer
        if self.isOptionValid('layer'):
            self._vtkrenderer.SetLayer(self.applyOption('layer'))

        # Viewport
        if self.isOptionValid('viewport'):
            self._vtkrenderer.SetViewport(self.applyOption('viewport'))

        # Background (only gets applied if layer=0)
        if self.isOptionValid('background'):
            self._vtkrenderer.SetBackground(self.applyOption('background'))

        if self.isOptionValid('background2'):
            self._vtkrenderer.SetBackground2(self.applyOption('background2'))

        if self.isOptionValid('gradient_background'):
            self._vtkrenderer.SetGradientBackground(self.applyOption('gradient_background'))

        # Camera
        if self.isOptionValid('camera'):
            self._vtkrenderer.SetActiveCamera(self.applyOption('camera'))

        #self._vtkrenderer.Render()

    def getBounds(self):
        """
        Return the bounding box of the results.
        """
        pass

    def _printCamera(self, *args):
        print '\n'.join(utils.print_camera(self._vtkrenderer.GetActiveCamera()))


    def onHighlight(self, value):
        pass
