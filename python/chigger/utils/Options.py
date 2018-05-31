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
from collections import OrderedDict
import traceback

from Option import Option

import mooseutils

class Options(object):
    """
    A warehouse for creating and storing options
    """

    def __init__(self):
        self.__options = OrderedDict()

    def __contains__(self, name):
        return name in self.__options

    def __iadd__(self, options):
        """
        Append another Option objects options into this container.

        Inputs:
           options[Options]: An instance of an Options object to append.
        """
        for key in options.keys():
            self.__options[key] = options.raw(key)
        return self

    def __str__(self):
        """
        Allows print to work with this class.
        """
        return self.string()


    def keys(self):
        """
        List of option names
        """
        return self.__options.keys()

    def raw(self, name):
        """
        Return the option class.

        Inputs:
            name[str]: The name of the Option to retrieve
        """
        return self.__options[name]

    def remove(self, name):
        self.__options.pop(name)

    def modified(self):
        """
        Returns True if any options have the applied flag set to False
        """
        return any(not opt.applied for opt in self.__options.values())

    #def pop(self, name, default=None):
    #    """
    #    Remove an Option object from the available options. (public)

    #    Inputs:
    #        name[str]: The name of the Option to retrieve
    #    """
    #    if not self.hasOption(name):
    #        return default
    #    else:
    #        option = self.__options.pop(name)
    #        return option.get() #pylint: disable=no-member

    def isOptionValid(self, name):
        """
        Test if the given option is valid (i.e., !None). (public)

        Inputs:
            name[str]: The name of the Option to retrieve
        """
        opt = self.__options.get(name, None)
        return (opt is not None) and (opt.value is not None) and (not opt.applied)

    #def setDefault(self, name, value):
    #    """
    #    Set the value and the default to the supplied value.

    #    Inputs:
    #        name[str]: The name of the Option to retrieve
    #        value: The value to set the option to
    #    """
    #    self.__options[name].setDefault(value)

    def set(self, name, value):
        """
        Overload for setting value of an option with [].

        Inputs:
            name[str]: The name of the Option to retrieve
            value: The value to set the option to
            **kwargs: Key, value pairs are passed to the Option object.
        """
        opt = self.__options.get(name, None)
        if opt is None:
            mooseutils.mooseWarning('No option with the name:', name)
        else:
            opt.value = value

    def get(self, name, apply=False):
        """
        Overload for accessing the parameter value by name with []

        Inputs:
            name[str]: The name of the Option to retrieve
        """
        opt = self.__options.get(name, None)
        if opt is None:
            msg = "Unknown option name: {}".format(name)
            mooseutils.mooseError(msg)
            return None
        elif apply:
            return opt.apply()
        else:
            return opt.value

    def applyOption(self, name):
        """
        Overload for accessing the parameter value by name with []

        Inputs:
            name[str]: The name of the Option to retrieve
        """
        return self.get(name, apply=True)

    def hasOption(self, name):
        """
        Test that the option exists.

        Inputs:
            name[str]: The name of the Option to retrieve
        """
        return name in self.__options

    def add(self, *args, **kwargs):
        """
        Add a new option to the warehouse

        Inputs:
            name[str]: The name of the option, used to access and set its value
            value: The value to set the property too (i.e., the default value)
            doc[str]: The documentation string

        Optional Key, value Pairs
            vtype: The type of the value
            allowed[list]: The allowed values
        """
        if args[0] in self.__options:
            mooseutils.mooseWarning('A parameter with the name', args[0], 'already exists.')
            return

        self.__options[args[0]] = Option(*args, **kwargs)

    def update(self, *args, **kwargs):
        """"
        Update the options given key, value pairs

        Inputs:
            *args: Options objects to use for updating this object.
            **kwargs: key, values pairs to used for updating this object.
        """

        # Unused options
        unused = set()

        # Update from Options object
        for opt in args:
            if not isinstance(opt, Options):
                mooseutils.mooseError("The supplied arguments must be Options objects or key, value pairs.")
            else:
                for key in opt.keys():
                    if self.hasOption(key):
                        if opt.isOptionValid(key):
                            self.set(key, opt.get(key))
                    else:
                        unused.add(key)

        # Update from kwargs
        for k, v in kwargs.iteritems():
            if k in self.__options:
                self.set(k, v)
            else:
                unused.add(k)

        # Warning for unused @todo warning
        if len(unused) > 0:
            msg = 'The following settings where not recognized:'
            for key in unused:
                msg += ' '*1 + key
            mooseutils.mooseError(msg)


    def string(self, **kwargs):
        """
        Functions to output the options to a string
        """
        return '\n\n'.join(str(opt) for opt in self.__options.values())

    def toScriptString(self, **kwargs):
        """
        Takes an Options object and returns a string for building python scripts.

        Inputs:
            kwargs: Key, value pairs provided will replace values in options with the string given
                    in the value.
        """
        output = []
        sub_output = dict()
        for key in self.keys():
            opt = self[key]

            if isinstance(opt, Options):
                items, _ = opt.toScriptString()
                if items:
                    sub_output[key] = items

            elif not self.isOptionDefault(key):
                if key in kwargs:
                    r = kwargs[key]
                else:
                    r = repr(opt)
                output.append('{}={}'.format(key, r))

        return output, sub_output


    # TODO: Move to ChiggerObject
    def printToScreen(self, **kwargs):


        output, sub_output = self.toScriptString(**kwargs)
        print 'setOptions({})'.format(', '.join(output))
        for key, value in sub_output.iteritems():
            print 'setOptions({}, {})'.format(key, ', '.join(value))

    def __isOptionDefault(self, name):
        """
        Test if the options is currently set to the default value.

        Inputs:
            name[str]: The name of the Option to retrieve
        """
        return self.hasOption(name) and \
               (self.__options[name].get() == self.__options[name].getDefault())
