import os
import sys
import glob
import importlib.util
import inspect
from .MooseObject import MooseObject

class Factory(object):
    """
    A class for instantiating python classes that inherit from factory.MooseObject.

    Inputs:
        *paths[str]: Names of python files or directories to be inspected for MooseObject classes
    """
    def __init__(self, *paths):

        # Create a list of all python files in the provided locations and/or filenames
        filenames = list()
        invalid = list()
        for path in paths:
            if os.path.isdir(path):
                filenames += glob.glob(os.path.join(path, '*.py'))
            elif os.path.isfile(path) and path.endswith('.py'):
                filenames.append(path)
            else:
                invalid.append(path)

        if invalid:
            msg = "The following paths were not located or are not python files, the supplied " \
                  "path must be a directory or a python file:"
            msg += '\n  '.join(invalid)
            raise OSError(msg)

        # Create map of text name to python class
        self.__objects = dict()
        for fname in filenames:
            self.__register_objects_from_file(fname)

    def create(self, type_name, *args, **kwargs):
        """
        Create an MooseObject given the name.

        Inputs:
            type_name[str]: Name of the class that is child of MooseObject to intantiate
            *args, **kwargs: Arguments for object contruction
        """
        if type_name not in self.__objects:
            msg = "Unknown MooseObject of type '{}', available types include:".format(type_name)
            msg += ", ".join(self.__objects.keys())
            raise OSError(msg)
        return self.__objects[type_name](*args, **kwargs)

    def __register_objects_from_file(self, file_path):
        """Registers all factory.MooseObject classes from the provided filename."""
        module_name, _ = os.path.splitext(file_path)
        print(module_name, file_path)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        print(spec)
        module = importlib.util.module_from_spec(spec)
        print(module)
        spec.loader.exec_module(module)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and (MooseObject in inspect.getmro(obj)):
                print(name, obj)
                self.__objects[name] = obj
