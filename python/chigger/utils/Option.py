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
import array
from collections import OrderedDict
import traceback
import mooseutils

class Option(object):
    """
    Storage container for an "option" that can be type checked.
    """

    def __init__(self, name, default=None, vtype=None, doc=None, allow=None, array=False):

        self.__name = name     # option name
        self.__value = None    # current value
        self.__default = None  # default value
        self.__vtype = vtype   # option type
        self.__allow = allow   # list of allowed values
        self.__applied = False # applies status, see Options class
        self.__doc = doc       # documentation string
        self.__array = array   # create an array

        if (self.__doc is not None) and (not isinstance(self.__doc, (str, unicode))):
            msg = "The supplied 'doc' argument must be a 'str' or 'unicode', but {} was provided.".format(type(self.__doc))
            raise TypeError(msg)

        if (self.__vtype is not None) and (not isinstance(self.__vtype, type)):
            msg = "The supplied 'vtype' argument must be a 'type', but {} was provided.".format(type(self.__vtype))
            raise TypeError(msg)


        if (self.__allow is not None) and (not isinstance(self.__allow, tuple)):
            msg = "The supplied 'allow' argument must be a 'tuple', but {} was provided.".format(type(self.__allow))
            raise TypeError(msg)


        if (self.__vtype is not None) and (self.__allow is not None):
            for value in self.__allow:
                if not isinstance(value, self.__vtype):
                    msg = "The supplied 'allow' argument must be a 'tuple' of {} items, but a {} item was provided.".format(self.__vtype, type(value))
                    raise TypeError(msg)

        if isinstance(default, tuple):
            self.__array = True

        if default is not None:
            self.value = default
            self.__default = default

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def default(self):
        return self.__default

    @property
    def applied(self):
        return self.__applied

    @property
    def doc(self):
        return self.__doc

    def apply(self):
        self.__applied = True
        return self.__value

    @value.setter
    def value(self, val):

        if val is None:
            self.__value = None
            return

        if self.__array and not isinstance(val, tuple):
            msg = "'{}' was defined as an array, which require {} for assignment, but a {} was provided."
            mooseutils.mooseWarning(msg.format(self.name, tuple, type(val)))
            return

        if self.__array:
            for v in val:
                if (self.__vtype is not None) and not isinstance(v, self.__vtype):
                    msg = "The values within '{}' must be of type {} but {} provided."
                    mooseutils.mooseWarning(msg.format(self.name, self.__vtype, type(v)))
                    return

        else:
            if (self.__vtype is not None) and not isinstance(val, self.__vtype):
                msg = "'{}' must be of type {} but {} provided."
                mooseutils.mooseWarning(msg.format(self.name, self.__vtype, type(val)))
                return

        # Check that the value is allowed
        if (self.__allow is not None) and (val != None) and (val not in self.__allow):
            msg = "Attempting to set '{}' to a value of {} but only the following are allowed: {}"
            mooseutils.mooseWarning(msg.format(self.name, val, self.__allow))
            return

        if self.__value != val:
            self.__applied = False

        self.__value = val



#@default.setter
#def default(self, val):
#    self.value = val
#    if val is None:
#        pass #TODO: Error...can't set default to None
#    else:
#        self.__default = val
#
