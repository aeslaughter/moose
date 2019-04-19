#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from .. import base
class ChiggerBackground(base.ChiggerResult):
    """
    An empty vtkRenderer to serve as the background for other objects.
    """
    __INTERACTIVE__ = False

    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()
        opt.remove('interactive')
        opt.add('background', (0., 0., 0.), vtype=float, size=3,
                doc="The background color, only applied when the 'layer' option is zero. A " \
                    "background result is automatically added when chigger.RenderWindow is " \
                    "utilized.")
        opt.add('background2', None, vtype=float, size=3,
                doc="The second background color, when supplied this creates a gradient " \
                    "background, only applied when the 'layer' option is zero. A background " \
                    "result is automatically added when chigger.RenderWindow is utilized.")
        opt.add('gradient_background', False,
                doc="Enable/disable the use of a gradient background.")

        opt.set('layer', 0)
        return opt

    def interactive(self):
        return False

    def applyOptions(self):

        if self.getOption('layer') != 0:
            msg = "The 'layer' option must be set to zero for background settings to apply."
            raise ValueError(msg)

        #self.setVTKOption('background', self._vtkrenderer.SetBackground)
        #self.setVTKOption('background2', self._vtkrenderer.SetBackground2)
        #self.setVTKOption('gradient_background', self._vtkrenderer.SetGradientBackground)
