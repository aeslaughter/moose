from chigger import base
from TextAnnotationSource import TextAnnotationSource

class TextAnnotation(base.ChiggerResult):
    """
    Meta class for creating ChiggerResult classes of different types.
    """
    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()
        opt += TextAnnotationSource.validOptions()
        return opt

    def __init__(self, **kwargs):
        print 'here'
        super(base.ChiggerResult, self).__init__(TextAnnotationSource(), **kwargs)



    """
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
    """
