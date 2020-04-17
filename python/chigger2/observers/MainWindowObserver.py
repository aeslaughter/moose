#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import re
import logging
import weakref
import textwrap
import vtk

import mooseutils
from parameters import InputParameters
from .ChiggerObserver import ChiggerObserver
from .. import utils
from .. import geometric


class Chigger3DInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera):
    def __init__(self):
        super(Chigger3DInteractorStyle, self).__init__()

class Chigger2DInteractorStyle(vtk.vtkInteractorStyleUser):
    ZOOM_FACTOR = 0.01

    def __init__(self):
        self.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.onMouseWheelForward)
        self.AddObserver(vtk.vtkCommand.MouseWheelBackwardEvent, self.onMouseWheelBackward)
        self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.onKeyPress)
        self.AddObserver(vtk.vtkCommand.KeyReleaseEvent, self.onKeyRelease)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.onMouseMove)
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.onLeftButtonPress)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.onLeftButtonRelease)
        super(Chigger2DInteractorStyle, self).__init__()

        self._source = None
        self._outline = None
        self._move_origin = None
        self._left_button_down = None

    def setSource(self, source, outline):
        self._source = source
        self._outline = outline
        self._left_button_down = True # method is called with the left-mouse button down

    def onLeftButtonPress(self, obj, event):
        self._left_button_down = True

    def onLeftButtonRelease(self, obj, event):
        self._left_button_down = False

    def onMouseWheelForward(self, obj, event):
        if not obj.GetShiftKey():
            factor = getattr(self._source, 'ZOOM_FACTOR', self.ZOOM_FACTOR)
            self._callSourceMethod('zoom', factor)
            bnds = self._source.getBounds()
            self._outline.setParams(bounds=bnds)
            obj.GetInteractor().GetRenderWindow().Render()

    def onMouseWheelBackward(self, obj, event):
        if not obj.GetShiftKey():
            factor = getattr(self._source, 'ZOOM_FACTOR', self.ZOOM_FACTOR)
            self._callSourceMethod('zoom', -factor)
            bnds = self._source.getBounds()
            self._outline.setParams(bounds=bnds)
            obj.GetInteractor().GetRenderWindow().Render()

    def onKeyPress(self, obj, event):
        key = obj.GetKeySym().lower()
        if key == 'shift_l':
            self._move_origin = obj.GetInteractor().GetEventPosition()

    def onKeyRelease(self, obj, event):
        key = obj.GetKeySym().lower()
        if key == 'shift_l':
            self._move_origin = None

    def onMouseMove(self, obj, event):
        if (self._move_origin is not None) and self._left_button_down:
            pos = obj.GetInteractor().GetEventPosition()
            if pos != self._move_origin:
                dx = pos[0] - self._move_origin[0]
                dy = pos[1] - self._move_origin[1]

                self._callSourceMethod('move', dx, dy)
                bnds = self._source.getBounds()
                self._outline.setParams(bounds=bnds)
                obj.GetInteractor().GetRenderWindow().Render()
                self._move_origin = pos

    def _callSourceMethod(self, method, *args, **kwargs):
        func = getattr(self._source, method, None)
        if func is not None:
            func(*args, **kwargs)


class MainWindowObserver(ChiggerObserver, utils.KeyBindingMixin):
    """
    The main means for interaction with the chigger interactive window.
    """
    RE = re.compile(r"(?P<key>[^\s=]+)=(?P<value>.*?)(?=(?:,\s[^\s=]+=|\Z)|\)\Z)")

    @staticmethod
    def validParams():
        opt = ChiggerObserver.validParams()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        bindings.add('v', MainWindowObserver._nextViewport, desc="Select the next Viewport object")
        bindings.add('v', MainWindowObserver._nextViewport, shift=True, args=(True,),
                     desc="Select the previous Viewport object")

        bindings.add('s', MainWindowObserver._nextSource,
                     desc="Select the next Source object")
        bindings.add('s', MainWindowObserver._nextSource, shift=True, args=(True,),
                     desc="Select the previous Source object")

        bindings.add('r', MainWindowObserver._deactivate, desc="Hard reset (clear) selection (resets the selection index)")
        bindings.add('r', MainWindowObserver._deactivate, desc="Soft reset (clear) selection (maintains the selection index)", shift=True, args=(True,))

        bindings.add('h', MainWindowObserver._printHelp, desc="Display the help for this object")
        bindings.add('q', MainWindowObserver._closeWindow, desc="Close the VTK window.")

        # TODO: Update _writeChanges to operate on all source and viewport objects and show
        #       a diff by default; use shift-w to write
        #bindings.add('w', MainWindowObserver._writeChanges, desc="Write the changed settings to the script file")
        return bindings

    def __init__(self, *args, **kwargs):

        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        # Disable th VTK default interaction
        mode = self._window.getParam('mode')
        if (mode is not None) and (mode != 'chigger'):
            self.warning("A MainWindowObserver object is being used but the 'mode' is set to " \
                         "something incompatible ('{}'), remove the 'mode' option from the " \
                         "Window object or set it to 'chigger'.", mode)

        self._window.setParam('mode', 'chigger')

        # Remove VTK key interactions
        self._window.getVTKInteractor().RemoveAllObservers()

        # Add the basic interaction for keys and mouse clicks
        self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent,
                                                    self._onKeyPressEvent)
        self._window.getVTKInteractor().AddObserver(vtk.vtkCommand.LeftButtonPressEvent,
                                                    self._onLeftButtonPressEvent)

        # The two available interaction styles to be used
        self.__style_2d = Chigger2DInteractorStyle()
        self.__style_3d = Chigger3DInteractorStyle()

        # Remove existing interaction to force the Viewport/Source to be active
        self._window.getVTKInteractor().SetInteractorStyle(None)

        # Storage for cycling through viewports and source objects
        self.__current_viewport_index = None
        self.__current_viewport_outline = None

        self.__current_source = None
        self.__current_source_index = None
        self.__current_source_outline = None

    def _availableViewports(self):
        return [viewport for viewport in self._window.viewports()]# if viewport.interactive]

    def _availableSources(self):
        sources = list()
        for viewport in self._availableViewports():
            sources += [(source, viewport) for source in viewport.sources()]
        return sources

    def _nextViewport(self, decrease=False): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Activate the "next" viewport object.
        """
        self.debug('_nextViewport')
        self._deactivateSource()
        self._deactivateViewport()

        viewports = self._availableViewports()
        N = len(viewports)
        if self.__current_viewport_index is None:
            self.__current_viewport_index = N - 1 if decrease else 0
        elif decrease:
            self.__current_viewport_index -= 1
            if self.__current_viewport_index < 0:
                self.__current_viewport_index = None
        else:
            self.__current_viewport_index += 1
            if self.__current_viewport_index == N:
                self.__current_viewport_index = None

        if self.__current_viewport_index is not None:
            viewport = viewports[self.__current_viewport_index]
            self._activateViewport(viewport)

    def _nextSource(self, decrease=False):
        """
        Keybinding callback: Activate the "next" source object in the current viewport
        """
        self.debug('_nextSource')
        self._deactivateSource()
        self._deactivateViewport()

        sources = self._availableSources()
        N = len(sources)
        if self.__current_source_index is None:
            self.__current_source_index = N - 1 if decrease else 0
        elif decrease:
            self.__current_source_index -= 1
            if self.__current_source_index < 0:
                self.__current_source_index = None
        else:
            self.__current_source_index += 1
            if self.__current_source_index == N:
                self.__current_source_index = None

        if self.__current_source_index is not None:
            source, viewport = sources[self.__current_source_index]
            self._activateSource(viewport, source)

    def _deactivate(self, soft=False): #pylint: disable=no-self-use, unused-argument
        """
        Keybinding callback: Deactivate all viewports/sourcs.
        """
        self.debug('_deactivate')
        self._deactivateViewport()
        self._deactivateSource()
        if not soft:
            self.__current_viewport_index = None
            self.__current_source_index = None

    def _activateViewport(self, viewport):
        self.debug('_activateViewport')
        self.__current_viewport_outline = geometric.Outline2D(viewport,
                                                              bounds=(0,1,0,1),
                                                              color=(1, 1, 0), linewidth=6)
        viewport.updateData()

    def _deactivateViewport(self):
        self.debug('_deactivateViewport')
        if self.__current_viewport_outline is not None:
            self.__current_viewport_outline.remove()
            self.__current_viewport_outline = None

    def _activateSource(self, viewport, source):
        self.debug('_activatesSource')
        if self.__current_source_outline is None:
            bnds = source.getBounds()
            obj = geometric.Outline2D if len(bnds) == 4 else geometric.Outline
            self.__current_source = source
            self.__current_source_outline = obj(viewport, bounds=bnds, color=(1, 1, 0))

            if isinstance(source.getVTKActor(), vtk.vtkActor2D):
                self.__style_2d.setSource(source, self.__current_source_outline)
                self._window.getVTKInteractor().SetInteractorStyle(self.__style_2d)
            else:
                self._window.getVTKInteractor().SetInteractorStyle(self.__style_3d)

            # Add the style resets the observers, thus re-enables key bindings on the
            # interactor. I am not sure why this, this is the work around to remove the default
            # VTK key bindings.
            self._window.getVTKInteractor().RemoveObservers(vtk.vtkCommand.CharEvent)

            # Disable interaction with all other viewports
            viewports = self._availableViewports()
            for vp in viewports:
                if vp is not viewport:
                    vp.getVTKRenderer().InteractiveOff()
                else:
                    vp.getVTKRenderer().InteractiveOn()

    def _deactivateSource(self):
        self.debug('_deactivateSource')
        if self.__current_source_outline is not None:

            if isinstance(self.__current_source.getVTKActor(), vtk.vtkActor2D):
                self.__style_2d.setSource(None, None)

            self.__current_source_outline.remove()
            self.__current_source_outline = None
            self.__current_source = None

            self._window.getVTKInteractor().SetInteractorStyle(None)

            # Restore interaction, to allow mouse clicks, with all viewports
            viewports = self._availableViewports()
            for vp in viewports:
                vp.getVTKRenderer().InteractiveOn()

    def _printHelp(self): #pylint: disable=unused-argument
        """
        Keybinding callback: Display the available controls for this object.
        """

        # Object name/type
        print(mooseutils.colorText('General Keybindings:', 'YELLOW'))
        self.printKeyBindings(self.keyBindings())

        if self.__current_viewport_index is not None:
            viewport = self._window.viewports()[self.__current_viewport_index]
            print(mooseutils.colorText('Current Viewport Keybindings ({}):'.format(viewport.name()), 'YELLOW'))
            self.printKeyBindings(viewport.keyBindings())

        if self.__current_source is not None:
            print(mooseutils.colorText('Current Source Keybindings ({}):'.format(self.__current_source.name()), 'YELLOW'))
            self.printKeyBindings(self.__current_source.keyBindings())

    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the vtkInteractor KeyPressEvent (see init).

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetKeySym().lower()
        shift = obj.GetShiftKey()
        self.debug('_onKeyPressEvent:{}:shift={}', key, shift)

        # This objects bindings
        for binding in self.getKeyBindings(key, shift):
            binding.function(self, *binding.args)

        # Viewport options
        if self.__current_viewport_index is not None:
            viewport = self._availableViewports()[self.__current_viewport_index]
            for binding in viewport.getKeyBindings(key, shift):
                binding.function(viewport, *binding.args)

        # Source options
        if self.__current_source is not None:
            for binding in self.__current_source.getKeyBindings(key, shift):
                binding.function(self.__current_source, *binding.args)

        self._window.updateInformation()
        self._window.getVTKWindow().Render()


    def _onLeftButtonPressEvent(self, obj, event):
        pos = self._window.getVTKInteractor().GetEventPosition()
        vtk_renderer = self._window.getVTKInteractor().FindPokedRenderer(*pos)
        props =  vtk_renderer.PickProp(*pos)

        #TODO: Check for more than one???
        #props.GetNumberOfItems()
        if props is not None:
            self._deactivateViewport()

            prop = props.GetFirstNode().GetViewProp()
            viewport, source = self._getSource(prop)
            if self.__current_source is not source:
                self._deactivateSource()

            if (source is not None) and (self.__current_source is None):
                self._activateSource(viewport, source)

        else:
            self._deactivateSource()

        self._window.updateInformation()
        self._window.getVTKWindow().Render()

    def _getSource(self, prop):
        for viewport in self._window.viewports():
            for source in viewport.sources():
                if source.getVTKActor() is prop:
                    return viewport, source
        return None

    def _closeWindow(self):
        ans = input('Close VTK window [y/N]? ')
        if ans.lower() in ('y', 'yes'):
            self._window.getVTKWindow().Finalize()
            self._window.getVTKInteractor().TerminateApp()

    def _writeChanges(self):
        if self.__current_source is None:
            return

        trace = self.__current_source._init_traceback[0]
        filename = trace[0]
        line = trace[1]

        output, sub_output = self.getNonDefaultParams(self._input_parameters)
        def sub_func(match):
            key = match.group('key')
            value = match.group('value')
            if key in output:
                return '{}={}'.format(key, repr(self.__current_source.getParam(key)))
            return match.group(0)

        with open(filename, 'r') as fid:
            lines = fid.readlines()

        content = self.RE.sub(sub_func, trace[3])
        lines[line-1] = '{}\n'.format(content)

        print(''.join(lines))
        #with open(filename, 'w+') as fid:
        #    fid.writelines(lines)
