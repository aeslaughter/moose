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
from ChiggerFilterBase import ChiggerFilterBase

class Calculator(ChiggerFilterBase):
    """
    Tool for perform calculations on input array data.
    """

    @staticmethod
    def getOptions():
        opt = ChiggerFilterBase.getOptions()
        opt.add('function', '1', "The function apply to the data (see vtk.vtkArrayCalculator).")
        opt.add('variables', [], "A list of variables to make available in the calculator function.")
        opt.add('result', None, "The name of the resulting computed variable.", vtype=str)
        return opt

    def __init__(self, **kwargs):
        super(Calculator, self).__init__(vtkfilter_type=vtk.vtkArrayCalculator, **kwargs)

    def update(self, **kwargs):
        """
        Update the bounds of the clipping box.
        """
        super(Calculator, self).update(**kwargs)
        for var in self.getOption('variable'):
            self._vtkfilter.AddScalarArrayName(var)

        self._vtkfilter.SetFunction(self.getOption('function'))
        self._vtkfilter.SetResultArrayName(self.getOption('result'))
