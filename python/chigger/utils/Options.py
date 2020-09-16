#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
from collections import OrderedDict
import copy
import mooseutils
import parameters
from .Option import Option

class Options(parameters.InputParameters):
    """
    A warehouse for creating and storing options
    """
    __PARAM_TYPE__ = Option

    def modified(self):
        """
        Returns the maximum modified time for the Option/Parameter objects
        """
        return max(opt.modified for opt in self._InputParameters__parameters.values())

    def assign(self, name, func):
        """
        Helper for assign values to a function, if they option is valid
        """
        if self.isValid(name):
            value = self.get(name)
            func(value)
