#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import os
import vtk
from .. import base

class Image(base.ChiggerSource2D):
    """
    Result object for displaying images in 3D space.
    """
    VTKMAPPERTYPE = vtk.vtkImageMapper


    @staticmethod
    def validOptions():
        """
        Return the default options for this object.
        """
        opt = base.ChiggerSource2D.validOptions()
        opt.add('filename', vtype=str, doc="The image filename to open.")
        opt.add('width', vtype=float,
                doc="The image width as a fraction of the window width "
                "(None maintains image dimension).")
        opt.add('height', vtype=float,
                doc="The image height as a fraction of the window width "
                    "(None maintains image dimension).")
        opt.add('position', (0, 0), vtype=float, size=2,
                doc="The position of the image within the viewport, in relative coordinates.")
        opt.add('horizontal_alignment', 'left', allow=('left', 'center', 'right'),
                doc="The position horizontal position alignment.")
        opt.add('vertical_alignment', 'bottom', allow=('bottom', 'center', 'top'),
                doc="The position vertical position alignment.")
        return opt


    """
    @staticmethod
    def validKeyBindings():
        bindings = base.ChiggerResult.validKeyBindings()
        bindings.add('w', Image._setWidth,
                     desc="Increase the scale of the image by 0.01.")
        bindings.add('w', Image._setWidth, shift=True,
                     desc="Decrease the scale of the image by 0.01.")
        bindings.add('a', Image._setOpacity,
                     desc="Increase the opacity (alpha) of the image by 0.05.")
        bindings.add('a', Image._setOpacity, shift=True,
                     desc="Decrease the opacity (alpha) of the image by 0.05.")
        return bindings
    """


    def __init__(self, *args, **kwargs):
        base.ChiggerSource2D.__init__(self, *args,
                                      nOutputPorts=1,
                                      outputType='vtkImageData',
                                      #outputType='vtkPolyData',
                                      **kwargs)

        self._reader = vtk.vtkPNGReader()
        self._resize = vtk.vtkImageResize()

    def _onRequestInformation(self, *args):

        self._vtkmapper.SetColorWindow(255); # width of the color range to map to
        self._vtkmapper.SetColorLevel(127.5); # center of the color range to map to

        filename = self.getOption('filename')
        if not os.path.exists(filename):
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logos',
                                                    os.path.basename(filename)))
        if not os.path.exists(filename):
            raise OSError('Unable to locate image file: {}'.format(self.getOption('filename')))

        _, ext = os.path.splitext(filename)
        if ext.lower() == '.png':
            self._reader = vtk.vtkPNGReader()
        else:
            raise OSError("The file format is not supported for the image file '{}', please use 'png'.".format(filename))

        self._reader.SetFileName(filename)
        self._resize.SetInputConnection(self._reader.GetOutputPort())

        base.ChiggerSource2D._onRequestInformation(self, *args)

        # TODO: I can not figure out why ChiggerSourceBase::__connectFilters is not making this connection
        self._vtkmapper.SetInputConnection(self._resize.GetOutputPort())

    def _onRequestData(self, inInfo, outInfo):
        base.ChiggerSource2D._onRequestData(self, inInfo, outInfo)

        # Set the width/height
        if self.isValid('width') or self.isValid('height'):
            window_size = self._viewport.getVTKRenderer().GetSize()
            self._reader.Update()
            extent = self._reader.GetDataExtent()
            image_size = [extent[1], extent[3], 0]
            aspect = float(image_size[0]) / float(image_size[1]) # w/h

            if self.isValid('width') and self.isValid('height'):
                image_size[0] = int(window_size[0] * self.getOption('width'))
                image_size[1] = int(window_size[1] * self.getOption('height'))

            elif self.isValid('width'):
                image_size[0] = int(window_size[0] * self.getOption('width'))
                image_size[1] = int(image_size[0] / aspect)

            elif self.isValid('height'):
                image_size[1] = int(window_size[1] * self.getOption('height'))
                image_size[0] = int(image_size[1] * aspect)

            self._resize.SetOutputDimensions(*image_size)

        # Image position
        if self.isValid('position'):

            # Determine the position in pixels
            tr = vtk.vtkCoordinate()
            tr.SetCoordinateSystemToNormalizedViewport()
            p = self.getOption('position')
            tr.SetValue(p[0], p[1], 0)
            position = list(tr.GetComputedDisplayValue(self._viewport.getVTKRenderer()))

            # Get the image size
            image_size = self._resize.GetOutputDimensions()
            if image_size == (-1, -1, -1):
                self._reader.Update()
                image_size = self._reader.GetOutput().GetDimensions()

            # Adjust the position for alignment
            if self.getOption('horizontal_alignment') == 'center':
                position[0] = position[0] - (image_size[0]*0.5)
            elif self.getOption('horizontal_alignment') == 'right':
                position[0] = position[0] - image_size[0]

            if self.getOption('vertical_alignment') == 'center':
                position[1] = position[1] - (image_size[1]*0.5)
            elif self.getOption('vertical_alignment') == 'top':
                position[1] = position[1] - image_size[1]

            self._vtkactor.SetPosition(*position)

        self._resize.Update()

        # TODO: This should setup the output of this object, but it doesn't do anything. For
        #       some reason the connection to the mapper is failing
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt.ShallowCopy(self._resize.GetOutput())

    def getBounds(self):
        position = self.getOption('position')
        width = self.getOption('width')
        if width is None:
            width = 1

        height = self.getOption('height')
        if height is None:
            height = 1
        return (position[0], position[0] + width, position[1], position[1] + height)


    # def setActive(self, active):
    #     """
    #     Overrides the default active highlighting.
    #     """
    #     if active:
    #         self._sources[0].getVTKActor().GetProperty().SetBackingColor(1, 0, 0)
    #         self._sources[0].getVTKActor().GetProperty().SetBacking(True)

    #     else:
    #         self._sources[0].getVTKActor().GetProperty().SetBacking(False)

    # def onMouseMoveEvent(self, position):
    #     """
    #     Re-position the image based on the mouse position.
    #     """
    #     self.setOption('position', position)
    #     self.printOption('position')

    # def _setWidth(self, window, binding): #pylint: disable=unused-argument
    #     """
    #     Callback for setting the image width.
    #     """
    #     step = -0.01 if binding.shift else 0.01
    #     width = self.getOption('width') + step
    #     if width > 0 and (width <= 1):
    #         self.setOption('width', width)
    #         self.printOption('width')

    # def _setOpacity(self, window, binding): #pylint: disable=unused-argument
    #     """
    #     Callback for changing opacity.
    #     """
    #     step = -0.05 if binding.shift else 0.05
    #     opacity = self.getOption('opacity') + step
    #     if opacity > 0 and opacity < 1:
    #         self.setOption('opacity', opacity)
    #         self.printOption('opacity')
