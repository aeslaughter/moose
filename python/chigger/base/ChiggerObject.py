#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import os
import sys
import re
import vtk
import logging
import traceback
import inspect
import mooseutils

class ChiggerObjectBase(object):
    """
    Base for all user-facing object in chigger.

    Inputs:
        **kwargs: key/value pairs that are used to update the options defined in the validOptions
                  method
    """
    __LOG_LEVEL__ = dict(critical=logging.CRITICAL, error=logging.ERROR, warning=logging.warning,
                         info=logging.INFO, debug=logging.DEBUG, notset=logging.NOTSET)

    @staticmethod
    def validOptions():
        """
        Objects should define a static validOptions method to add new key, value options.
        """
        from .. import utils # avoids cyclic dependencies
        opt = utils.Options()
        opt.add('name', vtype=str,
                doc="The object name (this name is displayed on the console help by pressing 'h'). "
                    "If a name is not supplied the class name is utilized.")
        return opt

    def __init__(self, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self._options = getattr(self.__class__, 'validOptions')()
        self.setOptions(**kwargs)
        self.__setOptionsFromCommandLine(sys.argv)
        self._options.validate()

        self._init_traceback = traceback.extract_stack()
        self._set_options_tracebacks = dict()

    def name(self):
        """
        Return the "name" of the object.

        If the 'name' option has been set, then it returns this value otherwise it returns the
        class name.
        """
        if not self.isOptionValid('name'):
            return self.__class__.__name__
        return self.getOption('name')

    def info(self, *args, **kwargs):
        """
        Log message with 'info' level.

        Inputs:
            msg[str]: Message to display
            *args[str]: optional strings to apply to message using 'format'
            **kwargs: key/value pairs passed to logging package
        """
        self._log(logging.INFO, *args, **kwargs)

    def debug(self, *args, **kwargs):
        """
        Log message with 'debug' level.

        see ChiggerObject.info
        """
        self._log(logging.DEBUG, *args, **kwargs)

    def warning(self, *args, **kwargs):
        """
        Log message with 'warning' level.

        see ChiggerObject.info
        """
        self._log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Log message with 'error' level.

        see ChiggerObject.info
        """
        self._log(logging.ERROR, *args, **kwargs)

    def isOptionValid(self, *args):
        """
        Test if the given option is valid (i.e., not None).
        """
        return self._options.isValid(*args)

    def isOptionDefault(self, *args):
        """
        Check if the option is set to the default value.
        """
        return self._options.isDefault(*args)

    def getOption(self, *args):
        """
        Return the value of an option.

        Inputs:
            name(s) [str]: Name(s) for option or nested option

        Examples:
            getOption('year')
            getOption('date', 'year') # 'date' is an InputParameters object
            getOption('date_year')    # 'date' is an InputParameters object
        """
        return self._options.get(*args)

    def setOption(self, *args):
        """
        Set a specific option or sub-option

        Inputs:
            name(s) [str]: Name(s) for option or nested option
            value: The value to assign to the option or nested option

        Examples:
            setOption('year', 1980)
            setOption('date', 'year', 1980) # 'date' is an InputParameters object
            setOption('date_year', 1980)    # 'date' is an InputParameters object
        """
        self.debug('setOption')
        self._options.set(*args)

    def setOptions(self, *args, **kwargs):
        """
        A method for setting/updating an objects options.

        Usage:
           setOptions(sub0, sub1, ..., key0=value0, key1=value1, ...)
           Updates all sub-options with the provided key value pairs

           setOptions(key0=value0, key1=value1, ...)
           Updates the main options with the provided key,value pairs
        """
        self.debug('setOptions')

        # Sub-options case
        if args:
            for sub in args:
                if not self._options.hasOption(sub):
                    msg = "The supplied sub-option '{}' does not exist.".format(sub)
                    mooseutils.mooseError(msg)
                else:
                    self._options.get(sub).update(**kwargs)
                    self._set_options_tracebacks[sub] = traceback.extract_stack()

        # Main options case
        else:
            self._options.update(**kwargs)

    def assignOption(self, *args):
        """
        Retrieve an option value and pass it into the given function
        """
        self.debug('assignOption')
        self._options.assign(*args)

    def printOption(self, key):
        """
        Prints the key/value pairing of an option as would be written in a script
        """
        print('{}={}'.format(key, repr(self.getOption(key))))

    def _log(self, lvl, msg, *args, **kwargs):
        """
        Helper for using logging package with class name prefix
        """
        name = self.getOption('name')
        msg = msg.format(*args)
        if name:
            self.__logger.log(lvl, '({}): {}'.format(self.getOption('name'), msg), **kwargs)
        else:
            self.__logger.log(lvl, ' {}'.format(msg), **kwargs)

    def __setOptionsFromCommandLine(self, argv):
        """
        Allow command-line modification of options upon during object construction.

        There are two syntax options:
            Type:Name:key=value
            Type:key=value
            The <name> is the value given to the 'name' option. If not provided then all objects of
            the type are changed.

        For example:
            Window:size=(500,400)
            Window:the_name_given:size=(500,400)
        """
        pattern = r'(?P<type>{}):(?:(?P<name>.*?):)?(?P<key>.*?)=(?P<value>.*)'.format(self.__class__.__name__)
        regex = re.compile(pattern)
        for arg in argv:
            match = re.search(regex, arg)
            if match and ((match.group('name') is None) or match.group('name') == self.name()):
                self.info('Setting Option from Command Line: {}'.format(match.group(0)))
                self.setOption(match.group('key'), eval(match.group('value')))

class ChiggerObject(ChiggerObjectBase):
    """
    Base class for objects that need options but are NOT in the VTK pipeline, for objects
    within the pipeline please use ChiggerAlgorithm.
    """

    def __init__(self, **kwargs):
        self.__modified_time = vtk.vtkTimeStamp()
        ChiggerObjectBase.__init__(self, **kwargs)
        self.__modified_time.Modified()

    def setOption(self, *args):
        """
        Set the supplied option, if anything changes mark the class as modified for VTK.

        See ChiggerObjectBase.setOption
        """
        ChiggerObjectBase.setOption(self, *args)
        if self._options.modified() > self.__modified_time.GetMTime():
            self.__modified_time.Modified()

    def setOptions(self, *args, **kwargs):
        """
        Set the supplied options, if anything changes mark the class as modified for VTK.

        See ChiggerObjectBase.setOptions
        """
        ChiggerObjectBase.setOptions(self, *args, **kwargs)
        if self._options.modified() > self.__modified_time.GetMTime():
            self.__modified_time.Modified()
