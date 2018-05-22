#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

#!/usr/bin/env python2
import sys
import textwrap
from collections import OrderedDict
import traceback
import mooseutils

class Option(object):
    """
    Storage container for an "option" that can be type checked.
    """

    def __init__(self, name, default=None, vtype=None, doc=None, allow=None):

        self.__name = name     # option name
        self.__value = None    # current value
        self.__default = None  # default value
        self.__vtype = vtype   # option type
        self.__allow = allow   # list of allowed values
        self.__applied = False # applies status, see Options class
        self.__doc = doc       # documentation string

        if default is not None:
            self.default = default

        if (self.__vtype is not None) and (not isinstance(self.__vtype, type)):
            msg = "The supplied 'vtype' argument must be a 'type', but {} was provided.".format(type(self.__vtype))
            raise TypeError(msg)


        if (self.__allow is not None) and (not isinstance(self.__allow, tuple)):
            msg = "The supplied 'allow' argument must be a 'tuple', but {} was provided.".format(type(self.__allow))
            raise TypeError(msg)


        """
        # Stored the supplied values
        # NOTE: The default and value are private to keep them from the type checking being
        # nullified if the values are just set directly.
        if len(args) == 2:
            self.name = args[0]
            self.__value = None
            self.doc = args[1]
            self.__default = None
        elif len(args) == 3:
            self.name = args[0]
            self.__value = args[1]
            self.doc = args[2]
            self.__default = self.__value
        else:
            raise Exception("Wrong number of arguments, must supply 2 or 3 input arguments.")

        # Extract optional settings
        self.vtype = kwargs.pop('vtype', type(self.__value))
        self.allow = kwargs.pop('allow', [])

        # Check that allow is correct type
        if not isinstance(self.allow, list):
            mooseutils.mooseWarning('The allow option must be supplied as a list.')

        # Check the allowed list contains the correct types
        else:
            for i in range(len(self.allow)):
                try:
                    if not isinstance(self.allow[i], self.vtype) and self.vtype != Option.ANY:
                        self.allow[i] = eval('{}({})'.format(self.vtype.__name__,
                                                             str(self.allow[i])))

                except: #pylint: disable=bare-except
                    msg = 'The type provided, {}, does not match the type of the allowed ' + \
                          'values, {} for the {} option.'
                    mooseutils.mooseWarning(msg.format(self.vtype.__name__,
                                                       type(self.allow[i]).__name__, self.name))
                    return

        # Try to set the value using the set method to test the type and if it is allowed
        if (self.__value != None) and not isinstance(self.__value, Options):
            self.set(self.__value)
        """

    @property
    def value(self):
        return self.__value

    @property
    def default(self):
        return self.__default

    @property
    def name(self):
        return self.__name

    def apply(self):
        self.__applied = True
        return self.__value

    @value.setter
    def value(self, val):
        print val, self.__allow

        if val is None:
            self.__value = None
            return

        if (self.__vtype is not None) and not isinstance(val, self.__vtype):
            msg = '{} must be of type {} but {} provided.'
            mooseutils.mooseWarning(msg.format(self.name, self.__vtype.__name__,
                                               type(val).__name__))
            return

        # Check that the value is allowed
        if (self.__allow is not None) and (val != None) and (val not in self.__allow):
            msg = 'Attempting to set {} to a value of {} but only the following are allowed: {}'
            mooseutils.mooseWarning(msg.format(self.name, val, self.__allow))
            return

        if self.__value != val:
            self.__applied = False

        self.__value = val


    @default.setter
    def default(self, val):
        self.value = val
        if val is None:
            pass #TODO: Error...can't set default to None
        else:
            self.__default = val
