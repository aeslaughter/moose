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
    @staticmethod
    def validOptions():
        opt = base.ChiggerResultBase.validOptions()
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
        opt.set('interactive', False)
        return opt

    def applyOptions(self):

        if self.getOption('layer') != 0:
            msg = "The 'layer' option must be set to zero for background settings to apply."
            raise ValueError(msg)

        #self.setVTKOption(self._vtkrenderer.SetBackground, 'background')
        #self.setVTKOption(self._vtkrenderer.SetBackground2, 'background2')
        #self.setVTKOption(self._vtkrenderer.SetGradientBackground, 'gradient_background')
