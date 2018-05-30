#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import vtk
from .. import utils
from .. import base

class TextAnnotationSource(base.ChiggerSourceBase):
    """
    Source for creating text annotations.
    """

    @staticmethod
    def validOptions():
        """
        Return default options for this object.
        """
        opt = base.ChiggerSourceBase.validOptions()
        #opt.add('position', (0.5, 0.5), "The text position within the viewport, in relative "
        #                                "coordinates.", vtype=float)
        opt.add('text', None, "The text to display.", vtype=str)
        #opt += utils.FontOptions.validOptions()
        return opt

    def __init__(self, **kwargs):
        super(TextAnnotationSource, self).__init__(vtkactor_type=vtk.vtkActor2D,
                                                   vtkmapper_type=vtk.vtkTextMapper, **kwargs)
        self._vtkactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()

    def update(self, **kwargs):
        """
        Updates the settings for the text creation. (override)
        """
        super(TextAnnotationSource, self).update(**kwargs)

        #utils.FontOptions.applyOptions(self._vtkmapper.GetTextProperty(), self._options)

        #if self.isOptionValid('position'):
        #    self._vtkactor.GetPositionCoordinate().SetValue(*self.applyOption('position'))

        if self.isOptionValid('text'):
        #    self._vtkmapper.GetTextProperty().Modified()
            self._vtkmapper.SetInput(self.applyOption('text'))
        #    print 'Setting text:', self.applyOption('text')

        # if options applied ... perform render
        #self._vtkrenderer.GetRenderWindow().Render()


    def onLeftButtonPressEvent(self, obj, event):

        if self._selected:
            self._selected = False
            self._vtkmapper.GetTextProperty().FrameOff()

        else:
            loc = obj.GetEventPosition()
            properties = self._vtkrenderer.PickProp(*loc)
            if properties:
                self._selected = True
                self._vtkmapper.GetTextProperty().FrameOn()

    def onMouseMoveEvent(self, obj, event):

        if self._selected:
            loc = obj.GetEventPosition()
            sz = self._vtkrenderer.GetSize()
            self.update(position=[loc[0]/float(sz[0]), loc[1]/float(sz[1])])
            self._vtkrenderer.GetRenderWindow().Render() #TODO: Handle this in update

    def onKeyPressEvent(self, obj, event):

        key = obj.GetKeySym()
        shift = obj.GetShiftKey()
        if shift and key == 'plus':
            prop = self._vtkmapper.GetTextProperty()
            sz = prop.GetFontSize()
            self.update(font_size=sz + 1)
            self._vtkrenderer.GetRenderWindow().Render() #TODO: Handle this in update

        elif shift and key == 'underscore':
            prop = self._vtkmapper.GetTextProperty()
            sz = prop.GetFontSize()
            if sz > 1:
                self.update(font_size=sz - 1)
                self._vtkrenderer.GetRenderWindow().Render() #TODO: Handle this in update

        elif shift and key == 'braceright':
            prop = self._vtkmapper.GetTextProperty()
            opacity = prop.GetOpacity()
            if opacity < 0.95:
                self.update(text_opacity=opacity + 0.05)
                self._vtkrenderer.GetRenderWindow().Render() #TODO: Handle this in update

        elif shift and key == 'braceleft':
            prop = self._vtkmapper.GetTextProperty()
            opacity = prop.GetOpacity()
            if opacity > 0.05:
                self.update(text_opacity=opacity - 0.05)
                self._vtkrenderer.GetRenderWindow().Render() #TODO: Handle this in update

        elif key == 'h':
            print 'help...'

        elif key == 'c':
            self._options.printToScreen()
            self._selected = False
            self._vtkmapper.GetTextProperty().FrameOff()
            self._vtkrenderer.GetRenderWindow().Render()
