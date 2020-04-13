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
import logging
import traceback
import mooseutils
from factory import MooseObject
from .. import utils

class ChiggerObjectBase(MooseObject):
    """
    Base for all user-facing object in chigger.

    This also follows the stack trace for when parameters are being set within the calling script
    to allow for dynamically changing the script while a VTK window is running.
    """

    @staticmethod
    def validParams():
        params = MooseObject.validParams()
        return params

    def __init__(self, *args, **kwargs):
        MooseObject.__init__(self, *args, **kwargs)
        self._init_traceback = traceback.extract_stack()
        self._set_options_tracebacks = dict()

    def setParam(self, name, value):
        """Set the value of an individual parameter."""
        self._input_parameters.set(name, value)

    def setParams(self, *args, **kwargs):
        """
        A method for setting/updating an objects options. (public)

        Usage:
           update(sub0, sub1, ..., key0=value0, key1=value1, ...)
           Updates all sub-options with the provided key value pairs

           update(key0=value0, key1=value1, ...)
           Updates the main options with the provided key,value pairs
        """
        # Sub-options case
        if args:
            for sub in args:
                if not self._input_parameters.hasParameter(sub):
                    msg = "The supplied sub-parameter '{}' does not exist.".format(sub)
                    mooseutils.mooseError(msg)
                else:
                    self._input_parameters.get(sub).update(**kwargs)
                    self._set_options_tracebacks[sub] = traceback.extract_stack()

        # Main options case
        else:
            self._input_parameters.update(**kwargs)

    def assignParam(self, name, func):
        """Apply the a parameter to the given function."""
        if self.isParamValid(name):
            value = self.getParam(name)
            func(value)

    def printParam(self, key):
        """Print key, value pair of a parameter."""
        print('{}={}'.format(key, repr(self.getParam(key))))

    def printParams(self, *args):
        """
        Print a list of all available options for this object.
        """
        print(self._options)

    def printSetParams(self, *args):
        """
        Print python code for the 'setParams' method.
        """
        output, sub_output = self._options.toScriptString()
        print('setParams({})'.format(', '.join(output)))
        for key, value in sub_output.items():
            print('setParams({}, {})'.format(key, ', '.join(repr(value))))

    def __del__(self):
        self.debug('__del__()')

class ChiggerObject(ChiggerObjectBase):
    """Base class for objects that need parameters but are NOT in the VTK pipeline."""

    def __init__(self, **kwargs):
        self.__modified_time = vtk.vtkTimeStamp()
        ChiggerObjectBase.__init__(self, **kwargs)
        self.__modified_time.Modified()

    def setParams(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        ChiggerObjectBase.setParams(self, *args, **kwargs)
        if self._options.modified() > self.__modified_time.GetMTime():
            self.__modified_time.Modified()
