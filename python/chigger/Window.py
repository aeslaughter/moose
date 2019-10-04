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
import sys
import logging
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import mooseutils

from . import base
from . import annotations
from . import observers
from .Viewport import Viewport


class Chigger3DInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera):
    pass

class Chigger2DInteractorStyle(vtk.vtkInteractorStyleUser):
    ZOOM_FACTOR = 2

    def __init__(self, source):
        self.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.onMouseWheelForward)
        self.AddObserver(vtk.vtkCommand.MouseWheelBackwardEvent, self.onMouseWheelBackward)
        self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.onKeyPressEvent)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.onMouseMoveEvent)

        super(Chigger2DInteractorStyle, self).__init__()

        self._source = source
        self._move_origin = None

    def onMouseWheelForward(self, obj, event):
        self.zoom(self.ZOOM_FACTOR)
        obj.GetInteractor().GetRenderWindow().Render()

    def onMouseWheelBackward(self, obj, event):
        self.zoom(-self.ZOOM_FACTOR)
        obj.GetInteractor().GetRenderWindow().Render()

    def onKeyPressEvent(self, obj, event):
        key = obj.GetKeySym().lower()
        if key == 'shift_l':
            self._shift_origin = obj.GetInteractor().GetEventPosition()

    def onMouseMoveEvent(self, obj, event):
        if obj.GetShiftKey():
            if self._move_origin == None:
                self._move_origin = obj.GetInteractor().GetEventPosition()
            else:
                pos = obj.GetInteractor().GetEventPosition()
                self.move(pos[0] - self._move_origin[0], pos[1] - self._move_origin[1])
                obj.GetInteractor().GetRenderWindow().Render()
                self._move_origin = pos


class ChiggerInteractor(vtk.vtkRenderWindowInteractor):
    def __init__(self, window):
        super(ChiggerInteractor, self).__init__()
        #vtk.vtkInteractorStyleJoystickCamera.__init__(self)

        #self.AddObserver(vtk.vtkCommand.KeyPressEvent, self._onKeyPressEvent)

        #self._window = window
        #window.UnRegister(self)

    #@staticmethod
    #def _onKeyPressEvent(obj, event):
    #    print obj._window


class Window(base.ChiggerAlgorithm):
    """
    Wrapper of vtkRenderWindow
    """
    ##__RESULTTYPE__ = base.ChiggerResult

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()

        opt.add('size', default=(1920, 1080), vtype=int, size=2,
                doc="The size of the window, expects a list of two items")
        opt.add('style', default='interactive', vtype=str,
                allow=('interactive', 'modal', 'interactive2D'),
                doc="The interaction style ('interactive' enables 3D interaction, 'interactive2D' "\
                    "disables out-of-plane interaction, and 'modal' disables all interaction.")
        opt.add('test', default='--test' in sys.argv, vtype=bool,
                doc="When True the interaction is disabled and the window closes immediately " \
                    "after rendering.")
        opt.add('offscreen', default=False, vtype=bool,
                doc="Enable offscreen rendering.")
        #opt.add('chigger', False, "Places a chigger logo in the lower left corner.") #TODO
        opt.add('smoothing', default=False, vtype=bool,
                doc="Enable VTK render window smoothing options.")
        opt.add('multisamples', vtype=int,
                doc="Set the number of multi-samples.")
        opt.add('antialiasing', default=0, vtype=int,
                doc="Number of antialiasing frames to perform (set vtkRenderWindow::SetAAFrames).")
        #opt.add('reset_camera', vtype=bool, default=True,
        #        doc="Automatically reset the camera clipping range on update.")

        # Background settings
        opt.add('background', (0.0, 0.0, 0.0), vtype=float, size=3,
                doc="The primary background color.")
        opt.add('background2', None, vtype=float, size=3,
                doc="The secondary background color, when specified a gradient style background is created.")
        opt.add('transparent', False, vtype=bool,
                doc="When True images created will use a transparent background.")
        return opt

    def __init__(self, *observers, **kwargs):
        base.ChiggerAlgorithm.__init__(self, nInputPorts=0, nOutputPorts=0,**kwargs)

        self.__vtkwindow = vtk.vtkRenderWindow()#kwargs.pop('vtkwindow', vtk.vtkRenderWindow())
        self.__vtkinteractor = kwargs.pop('vtkinteractor', self.__vtkwindow.MakeRenderWindowInteractor())
        self.__vtkinteractorstyle = None
        self.__viewports = list()

        Viewport(self, name='__ChiggerWindowBackground__', layer=0)

        # Create "chigger" watermark
        """
        self.__watermark = annotations.ImageAnnotation(filename='chigger_white.png',
                                                       width=0.025,
                                                       horizontal_alignment='left',
                                                       vertical_alignment='bottom',
                                                       position=[0, 0])
        """

    def add(self, viewport):
        #port = self.GetNumberOfInputPorts()
        #self.SetNumberOfInputPorts(port + 1)
        #self.SetInputConnection(port, viewport.GetOutputPort())

    #    #TODO: Type checking
        self.__viewports.append(viewport)

        renderer = viewport.getVTKRenderer()
        if not self.__vtkwindow.HasRenderer(renderer):
            self.__vtkwindow.AddRenderer(renderer)


    def updateInformation(self):
        base.ChiggerAlgorithm.updateInformation(self)
        for view in self.__viewports:
            view.updateInformation()

    def updateData(self):
        base.ChiggerAlgorithm.updateData(self)
        for view in self.__viewports:
            view.updateData()
            view.getVTKRenderer().ResetCamera()

    def viewports(self):
        """(public)
        Access to the Viewport objects.
        """
        return self.__viewports

#    def background(self):
#        return self.__viewports[0]

    def getVTKInteractor(self):
        """
        Return the vtkInteractor object.
        """
        return self.__vtkinteractor

    def getVTKInteractorStyle(self):
        """
        Return the vtkInteractor object.
        """
        return self.__vtkinteractorstyle

    def getVTKWindow(self):
        """
        Return the vtkRenderWindow object.
        """
        return self.__vtkwindow

    def start(self):
        """
        Begin the interactive VTK session.
        """
        self.debug("start")
        self.updateInformation()
        self.updateData()
        self.__vtkwindow.Render()
        if self.__vtkinteractor:
            self.__vtkinteractor.Initialize()
            self.__vtkinteractor.Start()

    #def __del__(self):
    #    base.ChiggerAlgorithm.__del__(self)
    #    for view in self.__viewports:
    #        del view
    #    self.__viewports = None

    def _onRequestInformation(self):
        base.ChiggerAlgorithm._onRequestInformation(self)

        # Viewport Layers
        n = self.__vtkwindow.GetNumberOfLayers()
        for view in self.__viewports:
            n = max(n, view.getOption('layer') + 1)
        self.__vtkwindow.SetNumberOfLayers(n)

        if self.isOptionValid('background'):
            self.__viewports[0].setOptions(background=self.getOption('background'),
                                           background2=self.getOption('background2'))

        # Auto Background adjustments
        """
        background = self.getOption('background')
        fontcolor = (0,0,0) if background == (1,1,1) else (1,1,1)
        for view in self.__viewports:
            for src in view.sources():
                if isinstance(src, base.ChiggerCompositeSource):
                    for s in src._sources:
                        for name in s.__BACKGROUND_OPTIONS__:
                            if not s.isOptionValid(name):
                                s.setOptions(**{name:fontcolor})
                else:
                    for name in src.__BACKGROUND_OPTIONS__:
                        if not src.isOptionValid(name):
                            src.setOptions(**{name:fontcolor})
        """

        self.assignOption('size', self.__vtkwindow.SetSize)


        test = self.getOption('test')
        style = self.getOption('style')
        if test:
            self.__vtkwindow.OffScreenRenderingOn()

        # TODO: Allow some basic interaction and have MainWindowObserver unset it, to allow
        #       for default VTK interaction if the observer is not used
        elif False:


            # TODO: Create  object in constructor, just setup things here based on 'style'
            #if self.__vtkinteractor is None:
            #    self.__vtkinteractor = self.__vtkwindow.MakeRenderWindowInteractor()
                #self.__vtkinteractor = ChiggerInteractor(self)
                #self.__vtkinteractor.SetRenderWindow(self.__vtkwindow)

            if style == 'interactive':
                self.__vtkinteractorstyle = vtk.vtkInteractorStyleJoystickCamera()
            elif style == 'interactive2d':
                self.__vtkinteractorstyle = vtk.vtkInteractorStyleImage()
            #elif style == 'modal':
            #    self.__vtkinteractorstyle = vtk.vtkInteractorStyleUser()

            self.__vtkinteractor.SetInteractorStyle(self.__vtkinteractorstyle)
            self.__vtkinteractor.RemoveObservers(vtk.vtkCommand.CharEvent)

            #main_observer = self.getOption('default_observer')
            #if main_observer is not None:
            #    main_observer.init(self)
            #    self._observers.add(main_observer)


        # vtkRenderWindow Settings
        self.assignOption('offscreen', self.__vtkwindow.SetOffScreenRendering)
        self.assignOption('smoothing', self.__vtkwindow.SetLineSmoothing)
        self.assignOption('smoothing', self.__vtkwindow.SetPolygonSmoothing)
        self.assignOption('smoothing', self.__vtkwindow.SetPointSmoothing)

        #self.setOption('antialiasing', self.__vtkwindow.SetAAFrames)
        self.assignOption('multisamples', self.__vtkwindow.SetMultiSamples)
        self.assignOption('size', self.__vtkwindow.SetSize)


        #self.__vtkwindow.Start()
        #print self.__vtkwindow

        #print self.getOption('background')
        #self.__background._options.update(self.getOption('background'))

        # Observers
        #if self.__vtkinteractor:

        #    for observer in self.getOption('observers'):
        #        if not isinstance(observer, observers.ChiggerObserver):
        #            msg = "The supplied observer of type {} must be a {} object."
        #            raise mooseutils.MooseException(msg.format(type(observer),
        #                                                       observers.ChiggerObserver))

        #        if observer not in self._observers:
        #            observer.init(self)
        #            self._observers.add(observer)

        #self._observer.init(self)

        #self.__vtkwindow.Render()

        """
        if self.getOption('reset_camera'):
            for result in self.__viewports:
                if result.isOptionValid('camera'):
                    result.getVTKRenderer().ResetCameraClippingRange()
                else:
                    result.getVTKRenderer().ResetCamera()
        """

    def _onRequestData(self, *args):
        base.ChiggerAlgorithm._onRequestData(self, *args)


        self.__vtkwindow.Render()
    #def setOptions(self, *args, **kwargs):
    #    base.ChiggerObject.setOptions(self, *args, **kwargs)
    #    self.__background._options.update(self.getOption('background'))

    def resetCamera(self):
        """
        Resets all the cameras.

        Generally, this is not needed but in some cases when testing the camera needs to be reset
        for the image to look correct.
        """
        for view in self.__viewports:
            view.getVTKRenderer().ResetCamera()

    def resetClippingRange(self):
        """
        Resets all the clipping range for open cameras.
        """
        for view in self.__viewports:
            view.getVTKRenderer().ResetCameraClippingRange()

    def write(self, filename, **kwargs):
        """
        Writes the VTKWindow to an image.
        """
        self.debug('write')

        # Allowed extensions and the associated readers
        writers = dict()
        writers['.png'] = vtk.vtkPNGWriter
        writers['.ps'] = vtk.vtkPostScriptWriter
        writers['.tiff'] = vtk.vtkTIFFWriter
        writers['.bmp'] = vtk.vtkBMPWriter
        writers['.jpg'] = vtk.vtkJPEGWriter

        # Extract the extension
        _, ext = os.path.splitext(filename)
        if ext not in writers:
            msg = "The filename must end with one of the following extensions: {}."
            self.error(msg, ', '.join(writers.keys()))
            return
        # Check that the directory exists
        dirname = os.path.dirname(filename)
        if (len(dirname) > 0) and (not os.path.isdir(dirname)):
            self.error("The directory does not exist: {}", dirname)
            return

        # Build a filter for writing an image
        window_filter = vtk.vtkWindowToImageFilter()
        window_filter.SetInput(self.__vtkwindow)

        # Allow the background to be transparent
        if self.getOption('transparent'):
            window_filter.SetInputBufferTypeToRGBA()

        self.__vtkwindow.Render()
        window_filter.Update()

        # Write it
        writer = writers[ext]()
        writer.SetFileName(filename)
        writer.SetInputData(window_filter.GetOutput())
        writer.Write()

    #def __getitem__(self, index):
    #    """
    #    Operator[] access into results objects.
    #    """
    #    return self.__viewports[index]


    def _onKeyPressEvent(self, obj, event):
        print('foo')
