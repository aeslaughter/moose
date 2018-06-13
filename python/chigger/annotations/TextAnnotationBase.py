from chigger import base
from TextAnnotationSource import TextAnnotationSource

class TextAnnotationBase(base.ChiggerResult):
    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()
        return opt

    def __init__(self, source, **kwargs):
        super(TextAnnotationBase, self).__init__(source, **kwargs)
        self.addKeyBinding('f', self._increaseFont, desc="Increase the font size by 1 point (when result is selected).")
        self.addKeyBinding('f', self._decreaseFont, shift=True, desc="Decrease the font size by 1 point (when result is selected).")
        self.addKeyBinding('o', self._increaseOpacity, desc="Increase the font opacity by 5% (when result is selected).")
        self.addKeyBinding('o', self._decreaseOpacity, shift=True, desc="Decrease the font opacity by 5% (when result is selected).")

        for src in self._sources:
            src.getVTKMapper().GetTextProperty().SetFrameColor(1,0,0)
            src.getVTKMapper().GetTextProperty().SetFrameWidth(3)

    def onActivate(self, window, active):
        super(TextAnnotationBase, self).onActivate(window, active)
        for src in self._sources:
            src.getVTKMapper().GetTextProperty().SetFrame(active)

    def _increaseFont(self, *args):
        sz = self.getOption('font_size') + 1
        self.update(font_size=sz)
        self.printOption('font_size')

    def _decreaseFont(self, *args):
        sz = self.getOption('font_size') - 1
        self.update(font_size=sz)
        self.printOption('font_size')

    def _increaseOpacity(self, *args):
        opacity = self.getOption('text_opacity') + 0.05
        if opacity <= 1.:
            self.update(text_opacity=opacity)
            self.printOption('text_opacity')

    def _decreaseOpacity(self, *args):
        opacity = self.getOption('text_opacity') - 0.05
        if opacity > 0.:
            self.update(text_opacity=opacity)
            self.printOption('text_opacity')

    def onMouseMoveEvent(self, position):
        self.update(position=position)
        self.printOption('position')
