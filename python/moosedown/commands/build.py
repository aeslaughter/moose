import os
import copy
import shutil
import logging
import anytree
import livereload
import importlib
import collections

import mooseutils
import hit

import moosedown

logging.basicConfig(level=logging.DEBUG) #TODO: need to get this into config
LOG = logging.getLogger(__name__)

# Set of extenions to load by default
DEFAULT_EXTENSIONS = ['moosedown.extensions.core',
                      'moosedown.extensions.config',
                      'moosedown.extensions.command',
                      'moosedown.extensions.include',
                      'moosedown.extensions.floats',
                      'moosedown.extensions.table',
                      'moosedown.extensions.autolink',
                      'moosedown.extensions.devel',
                      'moosedown.extensions.alert']

def command_line_options(subparser):
    build_parser = subparser.add_parser('build', help='Convert markdown into HTML or LaTeX.')

def params_to_dict(node):
    """
    TODO: move this to mooseutils
    """
    return {child.path():child.param() for child in node.children(node_type=hit.NodeType.Field)}

def load_extensions(node, filename):
    """
    Instatiates the Extension objects, with the configuration from the hit file, for passing
    into the Translator object.

    Inputs:
        node[hit.Node|None]: The [Extensions] section of the hit file.
    """

    # The key is the extension module name, value is a dict() of configuration options, which is populated
    # from the hit nodes and applied to the object via the make_extension method.
    ext_configs = collections.OrderedDict()
    if not (node and node.param('disable_defaults')):
        ext_configs = collections.OrderedDict()
        for key in DEFAULT_EXTENSIONS:
            ext_configs[key] = dict()

    # Process the [Extensions] block of the hit input, if it exists
    if node:
        # Update the extension conifigure options based on the content of the hit nodes
        for child in node.children(node_type=hit.NodeType.Section):
            ext_type = child.param('type')
            if ext_type is None:
                msg = "ERROR\n%s:%s\nThe section '%s' must contain a 'type' parameter."
                LOG.error(msg, filename, child.line(), child.fullpath())
            else:
                config = params_to_dict(child)
                config.pop('type')
                ext_configs[ext_type] = config

    # Build the Extension objects
    extensions = []
    for name, config in ext_configs.iteritems():
        try:
            module = importlib.import_module(name)
            if not hasattr(module, 'make_extension'):
                msg = "The supplied module '%s' must have a 'make_extension' function."
                LOG.error(msg, module.__name__)
            else:
                extensions.append(module.make_extension(**config))

        except ImportError as e:
            msg = "Failed to import the '%s' module.\n%s"
            LOG.error(msg, name, e.message)

    return extensions

def load_object(node, filename, default, *args):
    """
    Helper for loading moosedown objects: Reader, Renderer, Translator
    """

    if node:
        type_ = node.param('type')
        if type_ is None:
            msg = "ERROR\n%s:%s\nThe section '%s' must contain a 'type' parameter, using the default %s."
            LOG.error(msg, filename, node.line(), node.fullpath(), type(default).__name__)
        else:
            config = params_to_dict(node)
            config.pop('type')
            try:
                return eval(type_)(*args, **config)
            except NameError:
                param = node.find('type')
                msg = "ERROR\n%s:%s\nThe parameter '%s' must contain a valid object name, using the default %s."
                LOG.error(msg, filename, param.line(), param.fullpath())

    return default(*args)

def load_content(node, filename):
    if not node:
        msg = "The [Content] section is required within the configure file {}."
        raise KeyError(msg.format(filename))

    items = []
    for child in node.children(node_type=hit.NodeType.Section):
        content = child.param('content').split() if child.param('content') else []
        items.append(dict(root_dir=child.param('root_dir'), content=content))

    return moosedown.tree.build_page_tree.doc_tree(items)

def load_config(filename):

    # Read the config.hit file #TODO: error check on filename
    with open(filename) as f:
        content = f.read()
    node = hit.parse(filename, content)

    extensions = load_extensions(node.find('Extensions'), filename)
    reader = load_object(node.find('Reader'), filename, moosedown.base.MarkdownReader)
    renderer = load_object(node.find('Renderer'), filename, moosedown.base.MaterializeRenderer)
    translator = load_object(node.find('Translator'), filename, moosedown.base.Translator, reader, renderer, extensions)
    content = load_content(node.find('Content'), filename)

    return translator, content


def main():

    destination = os.path.join(os.getenv('HOME'), '.local', 'share', 'moose', 'site')
    logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.hit'

    # TODO: add this to config.hit and command line
    #LOG.setLevel(logging.DEBUG)

    translator, root = load_config(config_file)


    if False:
        from moosedown.tree import page
        filename = '/Users/slauae/projects/moosedown/docs/content/utilities/moosedown/core.md'
        node = page.MarkdownNode(source=filename)
        node.read()
        ast, html = translator.convert(node)
        #print ast
        #print html

    else:
        server = livereload.Server()
        for node in anytree.PreOrderIter(root):
            node.base = destination
            node.translator = translator

            if node.source and os.path.isfile(node.source):
                server.watch(node.source, node.build)

            # Everything needs translator before it can build
            node.build()

        server.serve(root=destination, port=8000)
