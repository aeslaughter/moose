"""
Tools for loading extensions from a list of strings and/or modules.
"""
import importlib
import types

from moosedown.common import exceptions
from check_type import check_type

def load_extensions(ext_list, ext_configs=None):
    """
    Convert the supplied list into MooseDocs extension objects by calling the make_extension method.
    """
    if ext_configs is None:
        ext_configs = dict()
    check_type('ext_list', ext_list, list)
    check_type('ext_configs', ext_configs, dict)

    extensions = []
    for ext in ext_list:
        name, mod = _get_module(ext)
        if not hasattr(mod, 'make_extension'):
            msg = "The supplied module {} does not contain the required 'make_extension' function."
            raise exceptions.MooseDocsException(msg, name)
        else:
            obj = mod.make_extension()
            obj.update(**ext_configs.get(name, dict()))
            extensions.append(obj)

    return extensions

def _get_module(ext):
    """
    Helper for loading a module.
    """
    if isinstance(ext, types.ModuleType):
        name = ext.__name__
    elif isinstance(ext, str):
        name = ext
        try:
            ext = importlib.import_module(name)
        except ImportError:
            msg = "Failed to import the supplied {} module."
            raise exceptions.MooseDocsException(msg, name)
    else:
        msg = "The supplied module ({}) must be a module type or a string, but a {} object "\
              "was provided."
        raise exceptions.MooseDocsException(msg, ext, type(ext))

    return name, ext
