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

from ..geometric import CubeSource
from ImageAnnotationSource import ImageAnnotationSource
from .. import base

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
                doc="The logo width as a fraction of the window width, this is ignored if 'scale' option is set.")
        opt.add('horizontal_alignment', 'center', allow=('left', 'center', 'right'),
                doc="The position horizontal position alignment.")
        opt.add('vertical_alignment', 'center', allow=('bottom', 'center', 'top'),
                doc="The position vertical position alignment.")
        opt.add('scale', None, vtype=float,
                doc="The scale of the image. (By default the image is scaled by the width.)")
        opt += ImageAnnotationSource.validOptions()
        return opt

    def __init__(self, **kwargs):
        super(ImageAnnotation, self).__init__(ImageAnnotationSource(), **kwargs)
        self._vtkcamera = self._vtkrenderer.MakeCamera()
        self._vtkrenderer.SetInteractive(False)

        self._highlight_box = CubeSource()


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

        # Image scale
        if self.isOptionValid('scale'):
            scale = self.getOption('scale')
        else:
            scale = float(window[0])/float(size[0]) * self.getOption('width')

        # Compute the camera distance
        angle = self._vtkcamera.GetViewAngle()
        d = window[1]*0.5 / math.tan(math.radians(angle*0.5))

        # Determine the image position
        if self.isOptionValid('position'):
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
        renderer.SetActiveCamera(self._vtkcamera)
        renderer.ResetCameraClippingRange()

    def onSelect(self, selected):
        super(ImageAnnotation, self).onSelect(selected)
        if selected:
            self._sources.append(self._box)

        elif self._box in self._sources:
            self._sources.remove(self._box)
