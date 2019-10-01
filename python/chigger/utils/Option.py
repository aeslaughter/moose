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
import vtk #TODO: Create a VTKOption and VTKOptions class for modified stuff
import textwrap
import mooseutils

class Option(object):
    """
    Storage container for an "option" that can be type checked, restricted, and documented.

    The meta data within this object is designed to be immutable, the only portion of this class
    that can be changed (without demangling) is the assigned value, via the value setter.

    Inputs:
        name[str]: The name of the option.
        default[]: The default value, if "vtype" is set the type must match.
        doc[str]: A documentation string, which is used in the option dump.
        vtype[type]: The python type that this option is to be restricted.
        allow[tuple]: A tuple of allowed values, if vtype is set the types within must match.
        array[bool]: Define the option as an "array", which if 'vtype' is set restricts the
                     values within the tuple to match types.
        size[int]: Defines the size of an array, setting size will automatically set the
                   array flag.
    """

    def __init__(self, name, default=None, doc=None, vtype=None, allow=None, size=None,
                 array=False):

        # Force vtype to be a tuple to allow multipe types to be defined
        if isinstance(vtype, type):
            vtype = (vtype,)

        self.__name = name       # option name
        self.__value = None      # current value
        self.__default = default # default value
        self.__vtype = vtype     # option type
        self.__allow = allow     # list of allowed values
        self.__modified = vtk.vtkTimeStamp()    # modified status, see Options class
        self.__modified.Modified()
        self.__doc = doc         # documentation string
        self.__array = array     # create an array
        self.__size = size       # array size


        if not isinstance(self.__name, str):
            msg = "The supplied 'name' argument must be a 'str', but {} was provided."
            raise TypeError(msg.format(type(self.__name)))

        if (self.__doc is not None) and (not isinstance(self.__doc, str)):
            msg = "The supplied 'doc' argument must be a 'str', but {} was provided."
            raise TypeError(msg.format(type(self.__doc)))

        if (self.__vtype is not None) and (any(not isinstance(v, type) for v in self.__vtype)):
            msg = "The supplied 'vtype' argument must be a 'type', but {} was provided."
            raise TypeError(msg.format(type(self.__vtype)))

        if (self.__allow is not None) and (not isinstance(self.__allow, tuple)):
            msg = "The supplied 'allow' argument must be a 'tuple', but {} was provided."
            raise TypeError(msg.format(type(self.__allow)))

        if (self.__vtype is not None) and (self.__allow is not None):
            for value in self.__allow:
                if not isinstance(value, self.__vtype):
                    msg = "The supplied 'allow' argument must be a 'tuple' of {} items, but a {} " \
                            "item was provided."
                    raise TypeError(msg.format(self.__vtype, type(value)))

        if (self.__size is not None) and (not isinstance(self.__size, int)):
            msg = "The supplied 'size' argument must be a 'int', but {} was provided."
            raise TypeError(msg.format(type(self.__size)))

        elif self.__size is not None:
            self.__array = True

        if default is not None:
            self.value = default

    @property
    def name(self):
        """Returns the option name."""
        return self.__name

    @property
    def value(self):
        """Returns the option value."""
        return self.__value

    @property
    def default(self):
        """Returns the default value for the option."""
        return self.__default

    @property
    def modified(self):
        """Returns the applied status."""
        if hasattr(self.__value, 'modified'):
            return self.__value.modified()
        return self.__modified.GetMTime()

    @property
    def doc(self):
        """Returns the documentation string."""
        return self.__doc

    @property
    def allow(self):
        """Returns the allowable values for the option."""
        return self.__allow

    @property
    def size(self):
        """Returns the size of the option."""
        return self.__size

    @property
    def vtype(self):
        """Returns the variable type."""
        return self.__vtype

    @value.setter
    def value(self, val):
        """
        Sets the value and performs a myriad of consistency checks.
        """

        if val is None:
            if self.__value is not None:
                self.__modified.Modified()
            self.__value = None
            return

        if self.__array and not isinstance(val, tuple):
            msg = "'{}' was defined as an array, which require {} for assignment, but a {} was " \
                  "provided."
            mooseutils.mooseWarning(msg.format(self.name, tuple, type(val)))
            return

        if self.__array:
            for v in val:
                if self.__vtype is not None:
                    try:
                        v = self.__vtype(v)
                    except (ValueError, TypeError):
                        pass

                if (self.__vtype is not None) and not isinstance(v, self.__vtype):
                    msg = "The values within '{}' must be of type {} but {} provided."
                    mooseutils.mooseWarning(msg.format(self.name, self.__vtype, type(v)))
                    return

            if self.__size is not None:
                if len(val) != self.__size:
                    msg = "'{}' was defined as an array with length {} but a value with length {} "\
                          "was provided."
                    mooseutils.mooseWarning(msg.format(self.name, self.__size, len(val)))
                    return

        else:
            if self.__vtype is not None:
                try:
                    val = self.__vtype(val)
                except (ValueError, TypeError):
                    pass

            if (self.__vtype is not None) and not isinstance(val, self.__vtype):
                msg = "'{}' must be of type {} but {} provided."
                mooseutils.mooseError(msg.format(self.name, self.__vtype, type(val)))
                return

        # Check that the value is allowed
        if (self.__allow is not None) and (val != None) and (val not in self.__allow):
            msg = "Attempting to set '{}' to a value of {} but only the following are allowed: {}"
            mooseutils.mooseWarning(msg.format(self.name, val, self.__allow))
            return

        if self.__value != val:
            self.__modified.Modified()

        self.__value = val

    def __str__(self):
        """
        Returns a string showing the current state of the option.
        """
        out = [mooseutils.colorText(self.name, 'YELLOW')]

        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = ' '*2
        wrapper.subsequent_indent = ' '*2
        wrapper.width = 100
        out += wrapper.wrap(self.doc)

        out += ['    Value:    {}'.format(repr(self.__value)),
                '    Default:  {}'.format(repr(self.__default)),
                '    Type:     {}'.format(self.__vtype),
                '    Modified: {}'.format(repr(self.modified)),
                '    Array:    {}'.format(repr(self.__array))]

        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = '    Allow:   '
        wrapper.subsequent_indent = ' '*len(wrapper.initial_indent)
        wrapper.width = 80
        out += wrapper.wrap(repr(self.__allow))

        return '\n'.join(out)
