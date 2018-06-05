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
        super(TextAnnotation, self).__init__(TextAnnotationSource(), **kwargs)
        self.addKeyBinding('f', self._increaseFont, desc="Increase the font size by 1 point (when result is selected).")
        self.addKeyBinding('f', self._decreaseFont, shift=True, desc="Decrease the font size by 1 point (when result is selected).")
        self.addKeyBinding('o', self._increaseOpacity, desc="Increase the font opacity by 5% (when result is selected).")
        self.addKeyBinding('o', self._decreaseOpacity, shift=True, desc="Decrease the font opacity by 5% (when result is selected).")

    def onSelect(self, active):
        self._sources[0].getVTKMapper().GetTextProperty().SetFrameColor(1,0,0)
        self._sources[0].getVTKMapper().GetTextProperty().SetFrameWidth(3)
        self._sources[0].getVTKMapper().GetTextProperty().SetFrame(active)

    def _increaseFont(self, *args):
        if self.isSelected():
            sz = self.getOption('font_size') + 1
            self.update(font_size=sz)
            self.printOption('font_size')

    def _decreaseFont(self, *args):
        if self.isSelected():
            sz = self.getOption('font_size') - 1
            self.update(font_size=sz)
            self.printOption('font_size')

    def _increaseOpacity(self, *args):
        if self.isSelected():
            opacity = self.getOption('text_opacity') + 0.05
            if opacity <= 1.:
                self.update(text_opacity=opacity)
                self.printOption('text_opacity')

    def _decreaseOpacity(self, *args):
        if self.isSelected():
            opacity = self.getOption('text_opacity') - 0.05
            if opacity > 0.:
                self.update(text_opacity=opacity)
                self.printOption('text_opacity')

    def onMouseMoveEvent(self, position):
        if self.isSelected():
            self.update(position=position)
            self.printOption('position')
