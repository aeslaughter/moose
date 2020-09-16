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
            self._outline.setOptions(bounds=bnds)
            obj.GetInteractor().GetRenderWindow().Render()

    def onMouseWheelBackward(self, obj, event):
        if not obj.GetShiftKey():
            factor = getattr(self._source, 'ZOOM_FACTOR', self.ZOOM_FACTOR)
            self._callSourceMethod('zoom', -factor)
            bnds = self._source.getBounds()
            self._outline.setOptions(bounds=bnds)
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
                self._outline.setOptions(bounds=bnds)
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
    def validOptions():
        opt = ChiggerObserver.validOptions()
        opt += utils.KeyBindingMixin.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()

        """
        bindings.add('v', MainWindowObserver._nextViewport, desc="Select the next viewport.")
        bindings.add('v', MainWindowObserver._nextViewport, shift=True, args=(True,),
                     desc="Select the previous viewport.")

        bindings.add('s', MainWindowObserver._nextSource,
                     desc="Select the next source in the current viewport.")
        bindings.add('s', MainWindowObserver._nextSource, shift=True, args=(True,),
                     desc="Select the previous source in the current viewport.")

        #bindings.add('t', MainWindowObserver._deactivate, desc="Clear selection(s).")
        bindings.add('h', MainWindowObserver._printHelp, desc="Display the help for this object.")
        bindings.add('w', MainWindowObserver._writeChanges, desc="Write the changed settings to the script file.")
        """

        return bindings

    def __init__(self, *args, **kwargs):
        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        self.addObserver(vtk.vtkCommand.KeyPressEvent, self._onKeyPressEvent)
        self.addObserver(vtk.vtkCommand.LeftButtonPressEvent, self._onLeftButtonPressEvent)

        self.__style_2d = Chigger2DInteractorStyle()
        self.__style_3d = Chigger3DInteractorStyle()

        # TODO: Warn if viewport or source is already highlighted



    def _availableViewports(self):
        """Complete list of available Viewport objects"""
        return [viewport for viewport in self._window.viewports() if viewport.interactive()]

    def _getActiveViewport(self):
        """Current active (highlighted) Viewport object"""
        for viewport in self._availableViewports():
            if viewport.getOption('highlight'):
                return viewport
        return None

    def _setActiveViewport(self, viewport):
        for vp in self._availableViewports():
            vp.setOptions(highlight=viewport is vp)

    def _availableSources(self):
        """Complete list of available ChiggerSourceBase objects"""
        return [source for viewport in self._availableViewports() for source in viewport.sources() if source.interactive()]

    def _getActiveSource(self):
        """Current active (highlighted) ChiggerSourceBase object"""
        for source in self._availableSources():
            if source.getOption('highlight'):
                return source
        return None

    def _setActiveSource(self, source):
        for s in self._availableSources():
            s.setOptions(highlight=s is source)


    def _nextSource(self, decrease=False):
        """
        Keybinding callback: Activate the "next" source object in the current viewport
        """
        self.debug('Select Next Source')

        # Remove Viewport selection
        self._setActiveViewport(None)

        # Determine the index of the ChiggerSourceBase to be set to active
        sources = self._availableSources()
        current = self._getActiveSource()
        if current is not None:
            index = sources.index(current)
            index = index - 1 if decrease else index + 1

        else:
            index = 0

        if index < len(sources):
            current = sources[index]
            self._setActiveSource(current)

        self._window.getVTKWindow().Render()

    def _onKeyPressEvent(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the vtkInteractor KeyPressEvent (see init).

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetKeySym().lower()
        shift = obj.GetShiftKey()
        self.debug('Key press: {}, shift={}', key, shift)

        # This objects bindings
        for binding in self.getKeyBindings(key, shift):
            binding.function(self, *binding.args)

        # Call the Window bindings
        for binding in self._window.getKeyBindings(key, shift):
            binding.function(self._window, *binding.args)


        # Viewport options
        #viewport = self._getActiveViewport()
        #if viewport is not None:
        #    for binding in viewport.getKeyBindings(key, shift):
        #        binding.function(viewport, *binding.args)

        # Source options
        #if self.__current_source_index is not None:
        #    viewport = self._availableViewports()[self.__current_viewport_index]
        #    source = self._availableSources(viewport)[self.__current_source_index]
        #    for binding in source.getKeyBindings(key, shift):
        #        binding.function(source, *binding.args)

        #self._window.Update()
        self._window.getVTKWindow().Render()


    def _onLeftButtonPressEvent(self, obj, event):

        return None

        pos = self._window.getVTKInteractor().GetEventPosition()
        vtk_renderer = self._window.getVTKInteractor().FindPokedRenderer(*pos)
        vtk_style = self._window.getVTKInteractorStyle()
        props = vtk_renderer.PickProp(*pos)

        """
        #TODO: Check for more than one???
        #props.GetNumberOfItems()
        if props is not None:
            prop = props.GetFirstNode().GetViewProp()
            viewport, source = self._getSource(prop)
            if self.__current_source is not source:
                self._deactivateSource()

            self._activateSource(viewport, source)

        else:
            self._deactivateSource()
        """

    def _writeChanges(self):
        return

        """
        if self.__current_source is None:
            return

        trace = self.__current_source._init_traceback[0]
        filename = trace[0]
        line = trace[1]

        output, sub_output = self.__current_source._options.getNonDefaultOptions()
        def sub_func(match):
            key = match.group('key')
            value = match.group('value')
            if key in output:
                return '{}={}'.format(key, repr(self.__current_source.getOption(key)))
            return match.group(0)

        with open(filename, 'r') as fid:
            lines = fid.readlines()

        content = self.RE.sub(sub_func, trace[3])
        lines[line-1] = '{}\n'.format(content)

        print(''.join(lines))
        """
