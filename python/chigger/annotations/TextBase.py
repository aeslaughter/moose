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
from .. import utils
class TextBase(base.ChiggerSource2D):
    """
    Base for text based annotations.
    """
    VTKACTORTYPE = vtk.vtkTextActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource2D.validOptions()
        opt += utils.TextOptions.validOptions()
        opt.add('text', vtype=str, doc="The text to display.")
        opt.add('position', vtype=float, size=2, doc="The text position in normalized viewport coordinates.")
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = base.ChiggerSource2D.validKeyBindings()
        bindings.add('f', TextBase._increaseFont,
                     desc="Increase the font size by 1 point.")
        bindings.add('f', TextBase._decreaseFont, shift=True,
                     desc="Decrease the font size by 1 point.")
        bindings.add('a', TextBase._increaseOpacity,
                     desc="Increase the font alpha (opacity) by 1%.")
        bindings.add('a', TextBase._decreaseOpacity, shift=True,
                     desc="Decrease the font alpha (opacity) by 1%.")
        return bindings

    def __init__(self, *args, **kwargs):
        base.ChiggerSource2D.__init__(self, *args, **kwargs)
        self._vtkactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()

    def _updateInformation(self, *args):
        base.ChiggerSource2D._updateInformation(self, *args)

        self.assignOption('text', self._vtkactor.SetInput)
        self.assignOption('position', self._vtkactor.SetPosition)
        utils.TextOptions.applyOptions(self._vtkactor.GetTextProperty(), self._options)

    def _increaseFont(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        sz = self.getOption('font_size') + 1
        #self.update(font_size=sz)
        self.printOption('font_size')

    def _decreaseFont(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        sz = self.getOption('font_size') - 1
        #self.update(font_size=sz)
        self.printOption('font_size')

    def _increaseOpacity(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        opacity = self.getOption('text_opacity') + 0.01
        if opacity <= 1.:
            #self.update(text_opacity=opacity)
            self.printOption('text_opacity')

    def _decreaseOpacity(self, *args): #pylint: disable=unused-argument
        """Keybinding method."""
        opacity = self.getOption('text_opacity') - 0.01
        if opacity > 0.:
            #self.update(text_opacity=opacity)
            self.printOption('text_opacity')
