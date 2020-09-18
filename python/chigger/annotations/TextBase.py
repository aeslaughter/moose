#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
from .. import base
class TextBase(base.ChiggerSource2D):
    """
    Base for text based annotations.
    """
    VTKACTORTYPE = vtk.vtkTextActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource2D.validOptions()
        opt.remove('camera')
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = base.ChiggerResult.validKeyBindings()
        bindings.add('f', TextAnnotationBase._increaseFont,
                     desc="Increase the font size by 1 point.")
        bindings.add('f', TextAnnotationBase._decreaseFont, shift=True,
                     desc="Decrease the font size by 1 point.")
        bindings.add('a', TextAnnotationBase._increaseOpacity,
                     desc="Increase the font alpha (opacity) by 1%.")
        bindings.add('a', TextAnnotationBase._decreaseOpacity, shift=True,
                     desc="Decrease the font alpha (opacity) by 1%.")
        return bindings

    def __init__(self, *args, **kwargs):
        base.ChiggerSource2D.__init__(self, t*args, **kwargs)
        self._vtkactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()

    def _increaseFont(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        sz = self.getOption('font_size') + 1
        self.update(font_size=sz)
        self.printOption('font_size')

    def _decreaseFont(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        sz = self.getOption('font_size') - 1
        self.update(font_size=sz)
        self.printOption('font_size')

    def _increaseOpacity(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        opacity = self.getOption('text_opacity') + 0.01
        if opacity <= 1.:
            self.update(text_opacity=opacity)
            self.printOption('text_opacity')

    def _decreaseOpacity(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        opacity = self.getOption('text_opacity') - 0.01
        if opacity > 0.:
            self.update(text_opacity=opacity)
            self.printOption('text_opacity')
