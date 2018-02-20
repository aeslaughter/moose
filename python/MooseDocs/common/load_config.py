"""Tool for loading MooseDocs config hit file."""
import collections
import copy
import types
import importlib
import logging

import mooseutils
import MooseDocs
from MooseDocs.common import check_type, exceptions

LOG = logging.getLogger(__name__)

# Set of extenions to load by default
DEFAULT_EXTENSIONS = ['MooseDocs.extensions.core',
                      'MooseDocs.extensions.config',
                      'MooseDocs.extensions.command',
                      'MooseDocs.extensions.include',
                      'MooseDocs.extensions.floats',
                      'MooseDocs.extensions.media',
                      'MooseDocs.extensions.listing',
                      'MooseDocs.extensions.table',
                      'MooseDocs.extensions.autolink',
                      'MooseDocs.extensions.devel',
                      'MooseDocs.extensions.alert',
                      'MooseDocs.extensions.katex',
                      'MooseDocs.extensions.appsyntax',
                      'MooseDocs.extensions.bibtex',
                      'MooseDocs.extensions.sqa']

def load_config(filename):
    """
    Read the config.hit file andb create the Translator object.
    """
    node = mooseutils.hit_load(filename)

    extensions = _hit_load_extensions(node.find('Extensions'), filename)
    reader = _hit_load_object(node.find('Reader'), filename, MooseDocs.base.MarkdownReader)
    renderer = _hit_load_object(node.find('Renderer'), filename, MooseDocs.base.MaterializeRenderer)
    translator = _hit_load_object(node.find('Translator'), filename, MooseDocs.base.Translator,
                             reader, renderer, extensions)
    content = _hit_load_content(node.find('Content'), filename)

    return translator, content

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
            obj = mod.make_extension(**ext_configs.get(name, dict()))
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
            msg = "Failed to import the supplied '{}' module."
            raise exceptions.MooseDocsException(msg, name)
    else:
        msg = "The supplied module ({}) must be a module type or a string, but a {} object "\
              "was provided."
        raise exceptions.MooseDocsException(msg, ext, type(ext))

    return name, ext

def _hit_load_extensions(node, filename):
    """
    Instatiates the Extension objects, with the configuration from the hit file, for passing
    into the Translator object.

    Inputs:
        node[HitNode|None]: The [Extensions] section of the hit file.
    """

    #TODO: handle common options from top level [Extensions]

    # The key is the extension module name, value is a dict() of configuration options, which is
    # populated from the hit nodes and applied to the object via the make_extension method.
    ext_configs = collections.OrderedDict()
    print 'NODE:', type(node)
    if (node is None) or ('disable_defaults' not in node):
        for ext in DEFAULT_EXTENSIONS:
            ext_configs[ext] = dict()

    # Process the [Extensions] block of the hit input, if it exists
    if node:
        for child in node:
            if 'type' not in child:
                msg = "ERROR\n%s:%s\nThe section '%s' must contain a 'type' parameter."
                LOG.error(msg, filename, child.line, child.fullpath)
            else:
                config = {k:v for k, v in child.iterparams()}
                ext_type = config.pop('type')
                if ext_type not in ext_configs:
                    ext_configs[ext_type] = dict()
                ext_configs[ext_type].update(config)

    # Build the Extension objects
    return load_extensions(ext_configs.keys(), ext_configs)

def _hit_load_object(node, filename, default, *args):
    """
    Helper for loading MooseDocs objects: Reader, Renderer, Translator
    """

    if node:
        if 'type' not in node:
            msg = "ERROR\n%s:%s\nThe section '%s' must contain a 'type' parameter, " \
                  "using the default %s."
            LOG.error(msg, filename, node.line, node.fullpath, type(default).__name__)
        else:
            config = {k:v for k, v in node.iterparams()}
            config.pop('type')
            try:
                return eval(node['type'])(*args, **config)
            except NameError:
                msg = "ERROR\n%s:%s\nThe parameter '%s' must contain a valid object name, using " \
                      "the default %s."
                LOG.error(msg, filename, node.line, node.fullpath)

    return default(*args)

def _hit_load_content(node, filename):
    """
    Load the [Content] block from the config.hit file.
    """
    if not node:
        msg = "The [Content] section is required within the configure file {}."
        raise KeyError(msg.format(filename))

    items = []
    for child in node:
        content = child['content'].split() if 'content' in child else []
        items.append(dict(root_dir=child['root_dir'], content=content))

    return MooseDocs.tree.build_page_tree.doc_tree(items)
