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


LOG = logging.getLogger(__name__)

# Set of extenions to load by default
DEFAULT_EXTENSIONS = set(['moosedown.extensions.core',
                          'moosedown.extensions.command',
                          'moosedown.extensions.include'])



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
    if (node and node.param('disable_defaults')):
        ext_configs = collections.defaultdict(dict)
    else:
        ext_configs = collections.defaultdict(dict)
        ext_configs.update({k:dict() for k in DEFAULT_EXTENSIONS})

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
                ext_configs[ext_type].update(config)

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
            msg = "Failed to import the '%s' module."
            LOG.error(msg, name)

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

    items = [params_to_dict(child) for child in node.children(node_type=hit.NodeType.Section)]
    return moosedown.tree.build_page_tree.doc_tree(items)



def load_config(filename):

    # Read the config.hit file #TODO: error check on filename
    with open(filename) as f:
        content = f.read()
    root = hit.parse(filename, content)

    extensions = load_extensions(node.find('Extensions'), filename)
    reader = load_object(node.find['Reader'], filename, moosedown.base.MarkdownReader)
    renderer = load_object(node.find['Renderer'], filename, moosedown.base.MaterializeRenderer)
    translator = load_object(node.find['Translator'], filename, moosedown.base.Translator, reader, renderer)
    content = load_content(node.find('Content'), filename)

    return translator, content



def main():
    #config = dict()
    #config['materialize'] = (False, 'Enable the use of the Materialize framework for HTML output.')
    #extensions = ['moosedown.extensions.core', 'moosedown.extensions.devel']

    #logging.basicConfig(level=logging.DEBUG)

    config_file = 'config.hit'
    config = load_config(config_file)

    """
    reader = moosedown.base.MarkdownReader()
    renderer = moosedown.base.MaterializeRenderer()

    extensions = [moosedown.extensions.core]
    translator = moosedown.base.Translator(reader, renderer, extensions)

    filename = '/Users/slauae/projects/moosedown/docs/content/utilities/moosedown/index.md'
    node = moosedown.tree.page.MarkdownNode(None, source=filename)
    node.build(translator)
    #translator.convert()
    """


    """

    destination = '/Users/slauae/.local/share/moose/site'
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    else:
        os.makedirs(destination)

    config_file = 'config.yml'


    data = load_config(config_file)
    root = moosedown.tree.build_page_tree.doc_tree(data['pages'].values())


    translator = data['translator'](data['reader'], data['renderer'], data['extensions'])

    if False:
        #print '    ROOT', root._path[0]
        idx = root.findall('index.md')[0]
        idx.read()
        #print idx.get_root()#root(-1)(0)(1)._path[0]
        ast, html = translator.convert(idx)
        print ast

        #translator.convert(ast)
    else:

        server = livereload.Server()
        root.name = '' #TODO: This should not be needed
        for node in anytree.PreOrderIter(root):
            node.base = destination
            node.translator = translator#TODO: formalize this with a Property

            if node.source and os.path.isfile(node.source):
                #print 'WATCH:', type(node), node.source
                #server.watch(node.source, lambda: node.build(translator))
                server.watch(node.source, node.build)

        # Everything needs translator before it can build
        for node in anytree.PreOrderIter(root):
            node.build(translator)


        server.serve(root=destination, port=8000)
    """
