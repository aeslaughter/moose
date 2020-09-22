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
from .Annotation import Annotation
from .. import geometric

class Image(Annotation):
    """
    Result object for displaying images in 3D space.
    """
    VTKMAPPERTYPE = vtk.vtkImageMapper

    @staticmethod
    def validOptions():
        """
        Return the default options for this object.
        """
        opt = Annotation.validOptions()
        opt.add('filename', vtype=str, doc="The image filename to open.")
        opt.add('width', vtype=float,
                doc="The image width as a fraction of the window width "
                "(None maintains image dimension).")
        opt.add('height', vtype=float,
                doc="The image height as a fraction of the window width "
                    "(None maintains image dimension).")
        opt.add('halign', 'left', allow=('left', 'center', 'right'),
                doc="The position horizontal position alignment.")
        opt.add('valign', 'bottom', allow=('bottom', 'center', 'top'),
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
        Annotation.__init__(self, *args,
                            nOutputPorts=1,
                            outputType='vtkImageData',
                            **kwargs)

        self._vtkactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        self._vtkactor.GetPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()

        self._vtkreader = vtk.vtkPNGReader()
        self._vtkresize = vtk.vtkImageResize()
        self._vtkresize.SetInputConnection(self._vtkreader.GetOutputPort())
        self._vtkresize.SetResizeMethodToOutputDimensions()

        # Re-draw image when the window changes
        self._viewport._window.getVTKWindow().AddObserver(vtk.vtkCommand.WindowResizeEvent,
                                                          lambda *args: self._onRequestInformation(*args))
    def _onRequestInformation(self, *args):

        self._vtkmapper.SetColorWindow(255);       # width of the color range to map to
        self._vtkmapper.SetColorLevel(127.5);      # center of the color range to map to
        self._vtkmapper.SetRenderToRectangle(True) # enables vtkActor2D::SetPosition

        filename = self.getOption('filename')
        if not os.path.exists(filename):
            raise OSError('Unable to locate image file: {}'.format(self.getOption('filename')))
        self._vtkreader.SetFileName(filename)

        # Set the width/height
        image_size = self._getImageSize()
        position = self._getPosition(image_size)
        self._vtkactor.SetPosition(position[0], position[1])
        self._vtkactor.SetWidth(image_size[0])
        self._vtkactor.SetHeight(image_size[1])

        # Resize the image for the current viewport
        tr = vtk.vtkCoordinate()
        tr.SetCoordinateSystemToNormalizedViewport()
        tr.SetValue(image_size[0], image_size[1], 0)
        sz = list(tr.GetComputedDisplayValue(self._viewport.getVTKRenderer()))
        self._vtkresize.SetOutputDimensions(sz[0], sz[1], 0)

        # Base class call, do this at the end to allow for _highlight to get the correct image size
        Annotation._onRequestInformation(self, *args)

        # TODO: I can not figure out why ChiggerSourceBase::__connectFilters is not making this connection
        self._vtkmapper.SetInputConnection(self._vtkresize.GetOutputPort())

    def _onRequestData(self, inInfo, outInfo):
        Annotation._onRequestData(self, inInfo, outInfo)

        # TODO: This should setup the output of this object, but it doesn't do anything. For
        #       some reason the connection to the mapper is failing
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt.ShallowCopy(self._vtkresize.GetOutput())

    def _getPosition(self, image_size):
        # Determine the position in viewport coordinates, accounting for alignment
        position = list(self.getOption('position'))

        # Adjust the position for alignment
        if self.getOption('halign') == 'center':
            position[0] = position[0] - (image_size[0]*0.5)
        elif self.getOption('halign') == 'right':
            position[0] = position[0] - image_size[0]

        if self.getOption('valign') == 'center':
            position[1] = position[1] - (image_size[1]*0.5)
        elif self.getOption('valign') == 'top':
            position[1] = position[1] - image_size[1]

        return position

    def _getImageSize(self):
        """Return the image size in viewport dimensions"""
        window_size = self._viewport.getVTKRenderer().GetSize()
        self._vtkreader.Update()
        extent = self._vtkreader.GetDataExtent()
        image_size = [extent[1]/window_size[0], extent[3]/window_size[1], 0]
        aspect = image_size[0] / image_size[1] # a = w/h

        if self.isValid('width') and self.isValid('height'):
            image_size[0] = self.getOption('width')
            image_size[1] = self.getOption('height')

        elif self.isValid('width'):
            image_size[0] = self.getOption('width')
            image_size[1] = image_size[0] / aspect # h = w / a

        elif self.isValid('height'):
            image_size[1] = self.getOption('height')
            image_size[0] = image_size[1] * aspect # w = h * a

        return image_size

    def _highlight(self):
        if self.getOption('highlight'):
            xmin, ymin = self._vtkactor.GetPosition()
            xmax = xmin + self._vtkactor.GetWidth()
            ymax = ymin + self._vtkactor.GetHeight()
            bounds = (xmin, xmax, ymin, ymax)

            if (self._outline is None):
                self._outline = geometric.Outline2D(self._viewport,
                                                    linewidth=3,
                                                    color=(1,1,0),
                                                    pickable=False,
                                                    interactive=False,
                                                    bounds=bounds)
            else:
                self._outline.setOption('bounds', bounds)

        elif (not self.getOption('highlight')) and (self._outline is not None):
            self._outline.remove()
            del self._outline
            self._outline = None


    # def _setWidth(self, window, binding):
    #     """
    #     Callback for setting the image width.
    #     """
    #     step = -0.01 if binding.shift else 0.01
    #     width = self.getOption('width') + step
    #     if width > 0 and (width <= 1):
    #         self.setOption('width', width)
    #         self.printOption('width')

    # def _setOpacity(self, window, binding):
    #     """
    #     Callback for changing opacity.
    #     """
    #     step = -0.05 if binding.shift else 0.05
    #     opacity = self.getOption('opacity') + step
    #     if opacity > 0 and opacity < 1:
    #         self.setOption('opacity', opacity)
    #         self.printOption('opacity')
