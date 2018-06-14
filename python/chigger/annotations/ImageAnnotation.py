#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import math
import vtk
import mooseutils
from ..geometric import CubeSource
from ImageAnnotationSource import ImageAnnotationSource
from .. import base
from .. import geometric

class ImageAnnotation(base.ChiggerResult):
    """
    Result object for displaying images in 3D space.

    Inputs:
        key,value pairs set the options for this object.
    """

    @staticmethod
    def validOptions():
        """
        Return the default options for this object.
        """
        opt = base.ChiggerResult.validOptions()
        opt.add('filename', None, "The PNG file to read, this can be absolute or relative path to "
                                  "a PNG or just the name of a PNG located in the chigger/logos "
                                  "directory.", vtype=str)
        opt.add('position', (0.5, 0.5), vtype=float, size=2,
                doc="The position of the image center within the viewport, in relative coordinates.")
        opt.add('width', 0.25, vtype=float,
                doc="The logo width as a fraction of the window width.")
        opt.add('horizontal_alignment', 'center', allow=('left', 'center', 'right'),
                doc="The position horizontal position alignment.")
        opt.add('vertical_alignment', 'center', allow=('bottom', 'center', 'top'),
                doc="The position vertical position alignment.")
        opt += ImageAnnotationSource.validOptions()
        return opt

    def __init__(self, **kwargs):
        super(ImageAnnotation, self).__init__(ImageAnnotationSource(), **kwargs)
        self._vtkcamera = self._vtkrenderer.MakeCamera()
        self._vtkrenderer.SetInteractive(False)
        self._vtkrenderer.SetActiveCamera(self._vtkcamera)

        self.addKeyBinding('w', self._setWidth, desc="Increase the scale of the image by 0.05.")
        self.addKeyBinding('w', self._setWidth, shift=True, desc="Decrease the scale of the image by 0.05.")
        self.addKeyBinding('o', self._setOpacity, desc="Increase the opacity of the image by 0.05.")
        self.addKeyBinding('o', self._setOpacity, shift=True, desc="Decrease the opacity of the image by 0.05.")

    def update(self, **kwargs):
        """
        Updates the 3D camera to place the image in the defined location.
        """
        super(ImageAnnotation, self).update(**kwargs)

        renderer = self.getVTKRenderer()

        # Coordinate transformation object
        tr = vtk.vtkCoordinate()
        tr.SetCoordinateSystemToNormalizedViewport()

        # Size of window
        window = renderer.GetRenderWindow().GetSize()

        # Size of image
        size = self._sources[-1].getVTKSource().GetOutput().GetDimensions()

        # Normalized image width
        scale = float(window[0])/float(size[0]) * self.getOption('width')

        # Compute the camera distance
        angle = self._vtkcamera.GetViewAngle()
        d = window[1]*0.5 / math.tan(math.radians(angle*0.5))

        # Determine the image position
        p = self.getOption('position')
        tr.SetValue(p[0], p[1], 0)
        position = list(tr.GetComputedDisplayValue(renderer))

        # Adjust for off-center alignments
        if self.getOption('horizontal_alignment') == 'left':
            position[0] = position[0] + (size[0]*0.5*scale)
        elif self.getOption('horizontal_alignment') == 'right':
            position[0] = position[0] - (size[0]*0.5*scale)

        if self.getOption('vertical_alignment') == 'top':
            position[1] = position[1] - (size[1]*0.5*scale)
        elif self.getOption('vertical_alignment') == 'bottom':
            position[1] = position[1] + (size[1]*0.5*scale)

        # Reference position (middle of window)
        tr.SetValue(0.5, 0.5, 0)
        ref = tr.GetComputedDisplayValue(renderer)

        # Camera offsets
        x = (ref[0] - position[0]) * 1/scale
        y = (ref[1] - position[1]) * 1/scale

        # Set the camera
        self._vtkcamera.SetViewUp(0, 1, 0)
        self._vtkcamera.SetPosition(size[0]/2. + x, size[1]/2. + y, d * 1/scale)
        self._vtkcamera.SetFocalPoint(size[0]/2. + x, size[1]/2. + y, 0)

        # Update the renderer
        renderer.ResetCameraClippingRange()

    def onActivate(self, window, active):
        """
        Activate/deactive highlighting for the image.
        """
        super(ImageAnnotation, self).onActivate(window, active)

        if active:
            self._sources[0].getVTKActor().GetProperty().SetBackingColor(1,0,0)
            self._sources[0].getVTKActor().GetProperty().SetBacking(True)

        else:
            self._sources[0].getVTKActor().GetProperty().SetBacking(False)

    def onMouseMoveEvent(self, position):
        """
        Re-position the image based on the mouse position.
        """
        self.setOption('position', position)
        self.update()

    def _setWidth(self, window, binding):
        """
        Callback for setting the image width.
        """
        step = -0.05 if binding.shift else 0.05
        width = self.getOption('width') + step
        if width > 0 and (width <= 1):
            self.setOption('width', width)
            self.printOption('width')

    def _setOpacity(self, window, binding):
        """
        Callback for changing opacity.
        """
        step = -0.05 if binding.shift else 0.05
        opacity = self.getOption('opacity') + step
        if opacity > 0 and opacity < 1:
            self.setOption('opacity', opacity)
            self.printOption('opacity')
