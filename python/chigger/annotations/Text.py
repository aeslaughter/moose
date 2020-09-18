#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
#pylint: enable=missing-docstring
from .TextBase import TextBase

class Text(TextBase):

    @staticmethod
    def validOptions():
        opt = TestBase.validOptions()
        #opt += utils.TextOptions.validOptions()
        opt.add('text', vtype=str, doc="The text to display.")
        opt.add('position', vtype=float, size=2, doc="The text position in normalized viewport coordinates.")
        return opt

    def _updateInformation(self, *args):
        TextBase._updateInformation(self, *args)

        self.assignOption('text', self._vtkactor.SetInput)
        #utils.TextOptions.applyOptions(self._vtkactor.GetTextProperty(), self._options)
        self.assignOption('position', self._vtkactor.SetPosition)
