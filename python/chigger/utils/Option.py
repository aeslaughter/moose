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
    Storage container for an "option" that can be type checked, restricted, and documented.

    The meta data within this object is designed to be immutable, the only portion of this class
    that can be changed (without demangling) is the assigned value, via the value setter.

    Inputs:
        name[str|unicode]: The name of the option.
        default[]: The default value, if "vtype" is set the type must match.
        doc[str|unicode]: A documentation string, which is used in the option dump.
        vtype[type]: The python type that this option is to be restricted.
        allow[tuple]: A tuple of allowed values, if vtype is set the types within must match.
        array[bool]: Define the option as an "array", which if 'vtype' is set restricts the
                     values within the tuple to match types.
        size[int]: Defines the size of an array, setting size will automatically set the
                   array flag.
    """

    def __init__(self, name, default=None, doc=None, vtype=None, allow=None, size=None, array=False):

        self.__name = name     # option name
        self.__value = None    # current value
        self.__default = None  # default value
        self.__vtype = vtype   # option type
        self.__allow = allow   # list of allowed values
        self.__applied = False # applies status, see Options class
        self.__doc = doc       # documentation string
        self.__array = array   # create an array
        self.__size = size     # array size

        if (self.__name is not None) and (not isinstance(self.__name, (str, unicode))):
            msg = "The supplied 'name' argument must be a 'str' or 'unicode', but {} was provided.".format(type(self.__name))
            raise TypeError(msg)

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

        if (self.__size is not None) and (not isinstance(self.__size, int)):
            msg = "The supplied 'size' argument must be a 'int', but {} was provided.".format(type(self.__size))
            raise TypeError(msg)

        elif self.__size is not None:
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

    @property
    def allow(self):
        return self.__allow

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

            if self.__size is not None:
                if (len(val) != self.__size):
                    msg = "'{}' was defined as an array with length {} but a value with length {} was provided."
                    mooseutils.mooseWarning(msg.format(self.name, self.__size, len(val)))
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

    def __str__(self):
        out = [mooseutils.colorText(self.name, 'YELLOW')]

        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = ' '*2
        wrapper.subsequent_indent = ' '*2
        wrapper.width = 100
        out += wrapper.wrap(self.doc)

        out += ['    Value:   {}'.format(repr(self.__value)),
                '    Default: {}'.format(repr(self.__default)),
                '    Type:    {}'.format(self.__vtype),
                '    Applied: {}'.format(repr(self.__applied)),
                '    Array:   {}'.format(repr(self.__array))]

        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = '    Allow:   '
        wrapper.subsequent_indent = ' '*len(wrapper.initial_indent)
        wrapper.width = 80
        out += wrapper.wrap(repr(self.__allow))

        return '\n'.join(out)
