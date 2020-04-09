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
from .. import utils

class ChiggerObjectBase(object):
    """
    Base for all user-facing object in chigger.

    The primary purpose is to provide a method for getting key, value
    options and consistent update methods.
    """
    __LOG_LEVEL__ = dict(critical=logging.CRITICAL, error=logging.ERROR, warning=logging.warning,
                         info=logging.INFO, debug=logging.DEBUG, notset=logging.NOTSET)

    @staticmethod
    def validOptions():
        """
        Objects should define a static validOptions method to add new key, value options. (public)
        """
        opt = utils.Options()
        opt.add('name', vtype=str,
                doc="The object name (this name is displayed on the console help by pressing 'h'). "
                    "If a name is not supplied the class name is utilized.")
        return opt

    def __init__(self, **kwargs):
        self.__log = logging.getLogger(self.__class__.__name__)
        self._options = getattr(self.__class__, 'validOptions')()
        self.setOptions(**kwargs)

        self._init_traceback = traceback.extract_stack()
        self._set_options_tracebacks = dict()

    def getLogger(self):
        return getattr(self, '__log', logging.getLogger(self.__class__.__name__))

    def _log(self, lvl, msg, *args):
        """Helper for using logging package with class name prefix"""
        obj = self.getLogger()
        name = self.getOption('name')
        if name:
            obj.log(lvl, '({}): {}'.format(self.getOption('name'), msg.format(*args)))
        else:
            obj.log(lvl, ' {}'.format(msg.format(*args)))

    def info(self, *args):
        self._log(logging.INFO, *args)

    def warning(self, *args):
        self._log(logging.WARNING, *args)

    def error(self, *args):
        self._log(logging.ERROR, *args)

    def debug(self, *args):
        self._log(logging.DEBUG, *args)

    def name(self):
        name = self.getOption('name')
        if name:
            return name
        return self.__class__.__name__

    #def updateOptions(self, other):
    #    self._options.update(other)

    def isOptionValid(self, name):
        """(public)
        Test if the given option is valid (i.e., not None).
        """
        return self._options.isOptionValid(name)

    def isOptionDefault(self, name):
        """(public)
        Check if the option is set to the default value.
        """
        return self._options.isOptionDefault(name)

    def getOption(self, name):
        """(public)
        Return the value of an option.

        Inputs:
            name[str]: The name of the option to retrieve
        """
        if name not in self._options:
            msg = "The {} object does not contain the '{}' option."
            mooseutils.mooseWarning(msg.format(self.getOption('name'), name))
            return None
        return self._options.get(name)

    def setOptions(self, *args, **kwargs):
        """
        A method for setting/updating an objects options. (public)

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

    def setOption(self, name, value):
        #self.debug('setOption')
        self._options.set(name, value)

    def assignOption(self, name, func):
        #self.debug('assignOption')
        self._options.assign(name, func)

    # TODO: ??? Move these to utils.show_options(obj, format=...)
    def printOption(self, key):
        print('{}={}'.format(key, repr(self.getOption(key))))

    def printOptions(self, *args):
        """
        Print a list of all available options for this object.
        """
        print(self._options)

    def printSetOptions(self, *args):
        """
        Print python code for the 'setOptions' method.
        """
        output, sub_output = self._options.toScriptString()
        print('setOptions({})'.format(', '.join(output)))
        for key, value in sub_output.items():
            print('setOptions({}, {})'.format(key, ', '.join(repr(value))))

    def __del__(self):
        self.debug('__del__()')

class ChiggerObject(ChiggerObjectBase):
    """Base class for objects that need options but are NOT in the VTK pipeline."""

    def __init__(self, **kwargs):
        self.__modified_time = vtk.vtkTimeStamp()
        ChiggerObjectBase.__init__(self, **kwargs)
        self.__modified_time.Modified()

    #def update(self, other):
    #    ChiggerObjectBase.update(self, other)
    #    if self._options.modified() > self.__modified_time.GetMTime():
    #        self.applyOptions()
    #        self.__modified_time.Modified()

    def setOptions(self, *args, **kwargs):
        """Set the supplied objects, if anything changes mark the class as modified for VTK."""
        ChiggerObjectBase.setOptions(self, *args, **kwargs)
        if self._options.modified() > self.__modified_time.GetMTime():
            self.__modified_time.Modified()
