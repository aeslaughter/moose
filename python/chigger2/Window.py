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

class Window(base.ChiggerAlgorithm):
    """
    Wrapper of vtkRenderWindow
    """

    @staticmethod
    def validParams():
        opt = base.ChiggerAlgorithm.validParams()

        opt.add('size', default=(1920, 1080), vtype=int, size=2,
                doc="The size of the window, in pixels, as a tuple (horizontal, vertical).expects a list of two items")
        #opt.add('style', default='interactive', vtype=str,
        #        allow=('interactive', 'modal', 'interactive2D'),
        #        doc="The interaction style ('interactive' enables 3D interaction, 'interactive2D' "\
        #            "disables out-of-plane interaction, and 'modal' disables all interaction.")
        #opt.add('test', default='--test' in sys.argv, vtype=bool,
        #        doc="When True the interaction is disabled and the window closes immediately " \
        #            "after rendering.")
        #opt.add('offscreen', default=False, vtype=bool,
        #        doc="Enable offscreen rendering.")

        opt.add('smoothing', default=False, vtype=bool,
                doc="Enable VTK render window smoothing options.")
        opt.add('multisamples', vtype=int,
                doc="Set the number of multi-samples.")
        opt.add('antialiasing', default=0, vtype=int,
                doc="Number of antialiasing frames to perform (set vtkRenderWindow::SetAAFrames).")

        # Background settings
        #opt.add('background', (0.0, 0.0, 0.0), vtype=float, size=3,
        #        doc="The primary background color.")
        #opt.add('background2', None, vtype=float, size=3,
        #        doc="The secondary background color, when specified a gradient style background is created.")
        #opt.add('transparent', False, vtype=bool,
        #        doc="When True images created will use a transparent background.")

        # Interaction
        opt.add('mode', default=None, vtype=str, allow=('vtk', 'chigger', 'offscreen', 'none'),
                doc="The Window object can operate in 4 modes that are defined with how the " \
                "various objects are being used: 'vtk' uses the native VTK interaction; " \
                "'chigger' is used if an Observer object (e.g., MainWindowObserver) is " \
                "instantiated directly in the script and manages the interaction completely; " \
                "'offscren' is used to render as such without interaction; and 'none' " \
                "render onscreen without interaction. Executing the script with " \
                "--test enables 'offscreen' as well. If the option is not set and a " \
                "MainWindowObserver object has not been created, then one will be created " \
                "automatically.")

        #opt.add('create_main_window_observer', default=True, vtype=bool,
        #        doc="Automatically create the MainWindowObserver object, if 'mode' is not set.")

        #opt.add('chigger', False, "Places a chigger logo in the lower left corner.") #TODO



        return opt

    def __init__(self, *observers, **kwargs):
        base.ChiggerAlgorithm.__init__(self, nInputPorts=0, nOutputPorts=0,**kwargs)

        self.__vtkwindow = vtk.vtkRenderWindow()
        self.__vtkinteractor = kwargs.pop('vtkinteractor', self.__vtkwindow.MakeRenderWindowInteractor())
        self.__vtkinteractorstyle = None
        self.__viewports = list()
        self.__main_observer = None

        # Set interaction mode
        if '--test' in sys.argv:
            self.setParam('mode', 'offscreen')

        # Add the background
        #Viewport(self, name='__ChiggerWindowBackground__', layer=0, interactive=False)

        # Create "chigger" watermark
        """
        self.__watermark = annotations.ImageAnnotation(filename='chigger_white.png',
                                                       width=0.025,
                                                       horizontal_alignment='left',
                                                       vertical_alignment='bottom',
                                                       position=[0, 0])
        """

    def add(self, viewport):
        """(public)

        """
        self.__viewports.append(viewport)
        self._addAlgorithm(viewport)

        renderer = viewport.getVTKRenderer()
        if not self.__vtkwindow.HasRenderer(renderer):
            self.__vtkwindow.AddRenderer(renderer)

    #def updateModified(self):
    #    base.ChiggerAlgorithm.updateModified(self)
    #    for view in self.__viewports:
    #        view.updateModified()

    #def updateInformation(self):
    #    base.ChiggerAlgorithm.updateInformation(self)
    #    for view in self.__viewports:
    #        view.updateInformation()

    def updateData(self):
        base.ChiggerAlgorithm.updateData(self)
        for view in self.__viewports:
            #view.updateData()
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
        return self.__vtkinteractor.GetInteractorStyle()

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
        self.updateObject()
        self.__vtkwindow.Render()
        if self.__vtkinteractor and self.getParam('mode') != 'offscreen':
            self.__vtkinteractor.Initialize()
            self.__vtkinteractor.Start()

    #def __del__(self):
    #    base.ChiggerAlgorithm.__del__(self)
    #    for view in self.__viewports:
    #        del view
    #    self.__viewports = None

    def _onRequestInformation(self, inInfo, outInfo):
        base.ChiggerAlgorithm._onRequestInformation(self, inInfo, outInfo)

        # Viewport Layers
        n = self.__vtkwindow.GetNumberOfLayers()
        for view in self.__viewports:
            n = max(n, view.getParam('layer') + 1)
        self.__vtkwindow.SetNumberOfLayers(n)

        #if self.isParamValid('background'):
        #    self.__viewports[0].setParams(background=self.getParam('background'),
        #                                  background2=self.getParam('background2'))

        # Auto Background adjustments
        """
        background = self.getParam('background')
        fontcolor = (0,0,0) if background == (1,1,1) else (1,1,1)
        for view in self.__viewports:
            for src in view.sources():
                if isinstance(src, base.ChiggerCompositeSource):
                    for s in src._sources:
                        for name in s.__BACKGROUND_OPTIONS__:
                            if not s.isParamValid(name):
                                s.setParams(**{name:fontcolor})
                else:
                    for name in src.__BACKGROUND_OPTIONS__:
                        if not src.isParamValid(name):
                            src.setParams(**{name:fontcolor})
        """

        self.assignParam('size', self.__vtkwindow.SetSize)

        # Create the MainWindowObserver if it doesn't exist and 'mode' is not set
        # The MainWindowObserver object sets the mode to 'chigger' for the next step
        #mode = self.getParam('mode')
        #if (mode is None) and (self.__main_observer is None):
        #    self.__main_observer = observers.MainWindowObserver(self)

        # Setup interaction: There are 4 basic modes to consider:
        #     1. Offscreen
        #     2. Default VTK interaction
        #     3. chigger based interaction (e.g. MainWindowObserver)
        #     4. no interaction
        mode = self.getParam('mode') # get it again because the MainWindowObserver can change it
        if mode == 'offscreen':
            self.__vtkwindow.OffScreenRenderingOn()

        # Use chigger interaction (MainWindowObserver handles this automatcially)
        elif (mode is None) or mode == 'chigger':
            self.__main_observer = observers.MainWindowObserver(self)

        # Use the default interaction, this is the default if MainWindowObserver doesn't exist
        elif mode == 'vtk':
            self.__vtkinteractorstyle = vtk.vtkInteractorStyleJoystickCamera()
            self.__vtkinteractor.SetInteractorStyle(self.__vtkinteractorstyle)

        elif mode == 'none':
            self.__vtkinteractor.SetInteractorStyle(None)
            self.__vtkinteractor.RemoveAllObservers()

        else: # this should be impossible to reach
            self.error("Invalid 'mode' of '{}' provided.", mode)

        # vtkRenderWindow Settings
        #self.assignParam('offscreen', self.__vtkwindow.SetOffScreenRendering)
        self.assignParam('smoothing', self.__vtkwindow.SetLineSmoothing)
        self.assignParam('smoothing', self.__vtkwindow.SetPolygonSmoothing)
        self.assignParam('smoothing', self.__vtkwindow.SetPointSmoothing)

        #self.setParam('antialiasing', self.__vtkwindow.SetAAFrames)
        self.assignParam('multisamples', self.__vtkwindow.SetMultiSamples)
        self.assignParam('size', self.__vtkwindow.SetSize)


        #self.__vtkwindow.Start()
        #print self.__vtkwindow

        #print self.getParam('background')
        #self.__background._options.update(self.getParam('background'))

        # Observers
        #if self.__vtkinteractor:

        #    for observer in self.getParam('observers'):
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
        if self.getParam('reset_camera'):
            for result in self.__viewports:
                if result.isParamValid('camera'):
                    result.getVTKRenderer().ResetCameraClippingRange()
                else:
                    result.getVTKRenderer().ResetCamera()
        """

    def _onRequestData(self, *args):
        base.ChiggerAlgorithm._onRequestData(self, *args)
        #self.__vtkwindow.Render()
    #def setParams(self, *args, **kwargs):
    #    base.ChiggerObject.setParams(self, *args, **kwargs)
    #    self.__background._options.update(self.getParam('background'))


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
        self.updateInformation()
        self.updateData()
        self.__vtkwindow.Render()

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
        #if self.getParam('transparent'):
        #    window_filter.SetInputBufferTypeToRGBA()

        self.__vtkwindow.Render()
        window_filter.Update()

        # Write it
        writer = writers[ext]()
        writer.SetFileName(filename)
        writer.SetInputData(window_filter.GetOutput())
        writer.Write()
