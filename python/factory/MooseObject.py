#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import logging

from parameters import InputParameters

class MooseObject(object):
    """
    Base class for objects requiring input parameters and logging.

    This class is designed to serve as the base for objects that will get their parameters
    from the factory system (i.e., TestHarness) and objects created by the user via scripts
    (e.g., chigger).
    """
    __LOG_LEVEL__ = dict(critical=logging.CRITICAL, error=logging.ERROR, warning=logging.warning,
                         info=logging.INFO, debug=logging.DEBUG, notset=logging.NOTSET)

    @staticmethod
    def validParams():
        """Default validParams."""
        params = InputParameters()
        params.add('name', vtype=str, doc="The name of the object.", mutable=False)
        params.add('error_mode', vtype=InputParameters.ErrorMode, mutable=False,
                   doc="Set InputParameters error mode to WARNING, ERROR, or EXCEPTION.")
        params.add('level', vtype=(str, int), doc="The logging level.", mutable=False)
        return params

    def __init__(self, *args, **kwargs):
        """
        Create a MooseObject with parameters.

        If an InputParameters object is not supplied, then validParams, of the child class, is
        called automatically at during construction.

        Inputs:
            *args [InputParameters]: Any number of InputParameters to be appended into single object
            **kwargs: Key/value pairs to be to the InputParameters object for this object

        Use:
           obj = InputParametersObject(params)
           obj = InputParametersObject(p0, p1)
           obj = InputParametersObject(year=1980, month=6)
           obj = InputParametersObject(p0, p1, p2, year=1980, month=6)
        """
        # logging object for helper functions
        self.__log = self.getLogger()

        # InputParameters for this MooseObject
        if len(args) == 1:
            self._input_parameters = args[0]
        elif len(args) > 1:
            self._input_parameters = args[0]
            for arg in args[1:]: # += all supplied InputParameters objects
                self._input_parameters += arg
        else:
            self._input_parameters = getattr(self.__class__, 'validParams')()

        # Update this objects params with key/value pairs
        self._input_parameters.update(**kwargs)

        # Check for missing required params, begin enforcing mutable keyword, etc.
        error_mode = self.getParam('error_mode') if 'error_mode' in self._input_parameters else None
        self._input_parameters.initialize(error_mode)

        # Store the name to avoid dict looks ups on name() method
        self.__name = self.getParam('name') if 'name' in self._input_parameters else None

        # Set the logging level
        if self._input_parameters.isValid('level'):
            self.__log.setLevel(self._input_parameters.get('level'))

    def name(self):
        """The name of the object as assigned using the 'name' parameter at construction."""
        return self.__name or self.__class__.__name__

    def parameters(self):
        """Return the InputParameters object."""
        return self._input_parameters

    def getParam(self, key):
        """Return the value of a parameter."""
        return self._input_parameters.get(key)

    def isParamValid(self, key):
        """Return validity of a parameter."""
        return self._input_parameters.isValid(key)

    def getLogger(self):
        """Return the logging object for this class."""
        return getattr(self, '__log', logging.getLogger(self.__class__.__name__))

    def info(self, *args, **kwargs):
        """Logging helper for 'info' level."""
        self._log(logging.INFO, *args)

    def warning(self, *args, **kwargs):
        """Logging helper for 'warning' level."""
        self._log(logging.WARNING, *args)

    def error(self, *args, **kwargs):
        """Logging helper for 'error' level."""
        self._log(logging.ERROR, *args)

    def debug(self, *args, **kwargs):
        """Logging helper for 'debug' level."""
        self._log(logging.DEBUG, *args)

    def _log(self, lvl, msg, *args, **kwargs):
        """Helper for using logging package with class name prefix"""
        obj = self.getLogger()
        if self.name() != self.__class__.__name__:
            obj.log(lvl, '({}):{}'.format(self.name(), msg.format(*args, **kwargs)))
        else:
            obj.log(lvl, msg.format(*args, **kwargs))
