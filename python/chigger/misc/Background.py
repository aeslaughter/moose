#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from ..Viewport import Viewport
class Background(Viewport):
    """
    An empty vtkRenderer to serve as the background for other objects.
    """
    __INTERACTIVE__ = False

    @staticmethod
    def validOptions():
        opt = Viewport.validOptions()
        opt.add('color', (0.0, 0.0, 0.0), vtype=float, size=3,
                doc="The primary background color.")
        opt.add('color2', None, vtype=float, size=3,
                doc="The secondary background color, when supplied this creates a gradient " \
                    "background")

        opt.remove('layer')
        opt.remove('light')
        opt.remove('camera')
        return opt

    def __init__(self, **kwargs):
        Viewport.__init__(self, **kwargs)

        self._vtkrenderer.SetLayer(0)

    def interactive(self):
        return False

    def applyOptions(self):
        Viewport.applyOptions(self)

        self._vtkrenderer.SetBackground(self.getOption('color'))
        if self.isOptionValid('color2'):
            self._vtkrenderer.SetBackground2(self.getOption('color2'))
            self._vtkrenderer.SetGradientBackground(True)
        else:
            self._vtkrenderer.SetGradientBackground(False)
