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

import base
import observers
import misc
import mooseutils

class ChiggerInteractorStyle(vtk.vtkInteractorStyleUser):
    def OnKeyPress(self, *args, **kwargs):
        print 'hello'
        pass


class RenderWindow(base.ChiggerObject):
    """
    Wrapper of VTK RenderWindow for use with ChiggerResultBase objects.
    """
    RESULT_TYPE = base.ChiggerResultBase

    @staticmethod
    def validOptions():
        opt = base.ChiggerObject.validOptions()

        opt.add('size', (960, 540), "The size of the window, expects a list of two items",
                vtype=int, size=2)
        opt.add('style', 'interactive', "The interaction style.", vtype=str,
                allow=('interactive', 'modal', 'interactive2D'))
        opt.add('test', False, "When True the interaction is disabled and the window closes "
                               "immediately after rendering.", vtype=bool)
        opt.add('offscreen', False, "Enable offscreen rendering.", vtype=bool)
        #opt.add('chigger', False, "Places a chigger logo in the lower left corner.") #TODO
        opt.add('smoothing', False, "Enable VTK render window smoothing options.", vtype=bool)
        opt.add('multisamples', None, "Set the number of multi-samples.", vtype=int)
        opt.add('antialiasing', 0, "Number of antialiasing frames to perform "
                                   "(set vtkRenderWindow::SetAAFrames).", vtype=int)

        # Observers
        opt.add('observers', [], "A list of ChiggerObserver objects, once added they are not " \
                                 "removed. Hence, changing the observers in this list will not " \
                                 "remove existing objects.", vtype=list)

        # Background settings
        background = misc.ChiggerBackground.validOptions()
        background.remove('layer')
        background.remove('camera')
        background.remove('viewport')
        opt += background
        return opt

    def __init__(self, *args, **kwargs):
        self.__vtkwindow = kwargs.pop('vtkwindow', vtk.vtkRenderWindow())
        self.__vtkinteractor = kwargs.pop('vtkinteractor', None)
        self.__vtkinteractorstyle = None

        super(RenderWindow, self).__init__(**kwargs)

        self._results = []
        self._observers = set()
        self.__active = None

        # Store the supplied result objects
        self.append(misc.ChiggerBackground(), *args)

    def __contains__(self, item):
        """
        'in' checks for result
        """
        return item in self._results

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

    def append(self, *args):
        """
        Append result object(s) to the window.
        """
        #self.setNeedsUpdate(True)
        for result in args:

            #result.setChiggerRenderWindow(self)
            # TODO: setRenderWindow() this will allow for keybinding/mouse events to have full control
            #result.getVTKRenderer().SetInteractive(False)

            # TODO: Add type checking mooseutils decorator


            mooseutils.mooseDebug('RenderWindow.append {}'.format(type(result).__name__))
            if isinstance(result, base.ResultGroup):
                self.append(*result.getResults())
            elif not isinstance(result, self.RESULT_TYPE):
                n = result.__class__.__name__
                t = self.RESULT_TYPE.__name__
                msg = 'The supplied result type of {} must be of type {}.'.format(n, t)
                raise mooseutils.MooseException(msg)
            self._results.append(result)

        self.update()


    def remove(self, *args):
        """
        Remove result object(s) from the window.
        """
        #self.setNeedsUpdate(True)
        for result in args:
            actors = result.getVTKRenderer().GetActors()
            for source in result.getSources():
                result.getVTKRenderer().RemoveActor(source.getVTKActor())

            if result.getVTKRenderer().GetActors().GetNumberOfItems() == 0:
                self.__vtkwindow.RemoveRenderer(result.getVTKRenderer())


            #if self.__vtkwindow.HasRenderer(result.getVTKRenderer()):
            #    self.__vtkwindow.RemoveRenderer(result.getVTKRenderer())
            if result in self._results:
                self._results.remove(result)

        # Reset active if it was removed
        if self.__active and (self.__active not in self._results):
            self.__active = None

        self.update()

    def clear(self):
        """
        Remove all objects from the render window.
        """
        self.remove(*self._results[1:])
        self.update()

    #def needsUpdate(self):
    #    """
    #    Returns True if the window or any of the child objects require update.
    #    """
    #    needs_update = base.ChiggerObject.needsUpdate(self)
    #    return needs_update or any([result.needsUpdate() for result in self._results])

    def setActive(self, result):
        """
        Set the active result object for interaction.
        """
        # If 'None' is supplied, disable the current result
        if result is None:
            if self.__active is not None:
                self.__active.onActivate(self, False)
                self.__active = None
            return

        # Check that the supplied result is available for activation
        if not result.getOption('interactive'):
            mooseutils.mooseError("The supplied result must be cable of interaction, i.e., the " \
                                  "'interactive' option must be True.")
            return

        if result not in self._results:
            mooseutils.mooseError("The active result must be added to the RendererWindow prior to " \
                                  "setting it as active.")
            return

        # Disable existing active result
        if self.__active is not None:
            self.__active.onActivate(self, False)

        # Set the supplied result as active and update the current renderer
        self.__active = result
        self.__active.onActivate(self, True)
        if self.__vtkinteractorstyle is not None:
            self.__vtkinteractorstyle.SetCurrentRenderer(self.__active.getVTKRenderer())

    def nextActive(self, reverse=False):

        step = 1 if not reverse else -1
        available = [result for result in self._results if result.getOption('interactive')]
        if (self.__active is None) and step == 1:
            self.setActive(available[0])
        elif (self.__active is None) and step == -1:
            self.setActive(available[-1])
        else:
            n = len(available)
            index = available.index(self.__active)
            index += step
            if (index == n) or (index == -1):
                self.setActive(None)
            else:
                self.setActive(available[index])

    def getActive(self):
        """
        Return the active result object.
        """
        return self.__active

    def start(self, timer=None):
        """
        Begin the interactive VTK session.
        """
        if timer:
            msg = "The timer argument is deprecated, please use the 'observers' setting."
            mooseutils.mooseWarning(msg)

        mooseutils.mooseDebug("{}.start()".format(self.__class__.__name__), color='MAGENTA')

        #if self.needsUpdate():
        self.update()

        if self.__vtkinteractor:
            self.__vtkinteractor.Initialize()
            self.__vtkinteractor.Start()

        #if self.getOption('style') == 'test':
        #    self.__vtkwindow.Finalize()

    def update(self, **kwargs):
        """
        Updates the child results and renders the results.
        """
        super(RenderWindow, self).update(**kwargs)

        # Setup interactor
        if self.isOptionValid('test') and self.getOption('test'):
            self.__vtkwindow.OffScreenRenderingOn()

        elif self.isOptionValid('style'):
            if self.__vtkinteractor is None:
                self.__vtkinteractor = self.__vtkwindow.MakeRenderWindowInteractor()

            style = self.getOption('style').lower()
            self.setOption('style', None) # avoids calling this function unless it changes
            if style == 'interactive':
                self.__vtkinteractorstyle = vtk.vtkInteractorStyleUser()
                #self.__vtkinteractorstyle = vtk.vtkInteractorStyleJoystickCamera()
            elif style == 'interactive2d':
                self.__vtkinteractorstyle = vtk.vtkInteractorStyleImage()
            elif style == 'modal':
                self.__vtkinteractorstyle = vtk.vtkInteractorStyleUser()

            self.__vtkinteractorstyle.SetInteractor(self.__vtkinteractor)

            #self.__vtkinteractorstyle.RemoveObserver(4)
            #int vtk.vtkCommand.KeyPressEvent

            #print self.__vtkinteractor
            self.__vtkinteractor.RemoveObservers(vtk.vtkCommand.CharEvent)
            #self.__vtkinteractorstyle.RemoveObservers(vtk.vtkCommand.KeyPressEvent)

            #self.__vtkinteractor.Disable()
            #self.__vtkinteractorstyle.SetEnabled(False)

            main_observer = observers.MainWindowObserver()
            main_observer.init(self)
            self._observers.add(main_observer)

            #print self.__vtkinteractorstyle
        # Background settings
        self._results[0].updateOptions(self._options)

        # vtkRenderWindow Settings
        if self.isOptionValid('offscreen'):
            self.__vtkwindow.SetOffScreenRendering(self.getOption('offscreen'))

        if self.isOptionValid('smoothing'):
            smooth = self.getOption('smoothing')
            self.__vtkwindow.SetLineSmoothing(smooth)
            self.__vtkwindow.SetPolygonSmoothing(smooth)
            self.__vtkwindow.SetPointSmoothing(smooth)

        if self.isOptionValid('antialiasing'):
            self.__vtkwindow.SetAAFrames(self.getOption('antialiasing'))

        if self.isOptionValid('multisamples'):
            self.__vtkwindow.SetMultiSamples(self.getOption('multisamples'))

        if self.isOptionValid('size'):
            self.__vtkwindow.SetSize(self.applyOption('size'))

        #self.__vtkwindow.Render()

        # Setup the result objects
        n = self.__vtkwindow.GetNumberOfLayers()
        for result in self._results:
            renderer = result.getVTKRenderer()
            if not self.__vtkwindow.HasRenderer(renderer):
                self.__vtkwindow.AddRenderer(renderer)
            #if result.needsUpdate():
            #result.initialize()
            result.update()
            n = max(n, renderer.GetLayer() + 1)

        # TODO: set if changed only
        self.__vtkwindow.SetNumberOfLayers(n)

        #if (self.__active is None) and len(self._results) > 0:
        #    self.setActive(self._results[0])

        # Observers
        if self.__vtkinteractor:

            for observer in self.getOption('observers'):
                if not isinstance(observer, observers.ChiggerObserver):
                    msg = "The supplied observer of type {} must be a {} object."
                    raise mooseutils.MooseException(msg.format(type(observer),
                                                               observers.ChiggerObserver))

                if observer not in self._observers:
                    observer.init(self)
                    self._observers.add(observer)



        for result in self._results:
            result.update()
        #print self.__vtkinteractor

        self.__vtkwindow.Render()

    def resetCamera(self):
        """
        Resets all the cameras.

        Generally, this is not needed but in some cases when testing the camera needs to be reset
        for the image to look correct.
        """
        for result in self._results:
            result.getVTKRenderer().ResetCamera()

    def write(self, filename, dialog=False, **kwargs):
        """
        Writes the VTKWindow to an image.
        """
        mooseutils.mooseDebug('RenderWindow.write()', color='MAGENTA')


        # TODO: Deactive and re-activate

        #if self.needsUpdate() or kwargs:
        self.update(**kwargs)

        # Allowed extensions and the associated readers
        writers = dict()
        writers['.png'] = vtk.vtkPNGWriter
        writers['.ps'] = vtk.vtkPostScriptWriter
        writers['.tiff'] = vtk.vtkTIFFWriter
        writers['.bmp'] = vtk.vtkBMPWriter
        writers['.jpg'] = vtk.vtkJPEGWriter

        # Extract the extensionq
        _, ext = os.path.splitext(filename)
        if ext not in writers:
            w = ', '.join(writers.keys())
            msg = "The filename must end with one of the following extensions: {}.".format(w)
            mooseutils.mooseError(msg, dialog=dialog)
            return

        # Check that the directory exists
        dirname = os.path.dirname(filename)
        if (len(dirname) > 0) and (not os.path.isdir(dirname)):
            msg = "The directory does not exist: {}".format(dirname)
            mooseutils.mooseError(msg, dialog=dialog)
            return

        # Build a filter for writing an image
        window_filter = vtk.vtkWindowToImageFilter()
        window_filter.SetInput(self.__vtkwindow)
        window_filter.Update()

        # Write it
        writer = writers[ext]()
        writer.SetFileName(filename)
        writer.SetInputData(window_filter.GetOutput())
        writer.Write()

    def __getitem__(self, index):
        """
        Operator[] access into results objects.
        """
        return self._results[index]
