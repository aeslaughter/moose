#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

#!/usr/bin/env python3
import vtk #TODO: Create a VTKOption and VTKOptions class for modified stuff
import textwrap
import mooseutils
import parameters

class Option(parameters.Parameter):
    """
    Custom Parameter object that includes modified time.
    """

    def __init__(self, *args, **kwargs):
        parameters.Parameter.__init__(self, *args, **kwargs)
        self.__modified = vtk.vtkTimeStamp()    # modified status, see Options class
        self.__modified.Modified()

    @property
    def modified(self):
        """Returns the applied status."""
        if hasattr(self._Parameter__value, 'modified'):
            return self._Parameter__value.modified()
        return self.__modified.GetMTime()

    @property
    def value(self):
        """Returns the option value."""
        return parameters.Parameter.value.fget(self)

    @value.setter
    def value(self, val):
        """
        Sets the value and performs a myriad of consistency checks and updates modified time
        """
        parameters.Parameter.value.fset(self, val)
        if self._Parameter__value != val:
            self.__modified.Modified()
