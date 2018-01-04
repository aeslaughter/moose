import os
import copy
import shutil
import logging
import anytree
import livereload
import importlib

import mooseutils
import hit

import moosedown

# Set of extenions to load by default
DEFAULT_EXTENSIONS = set(['moosedown.extensions.core',
                          'moosedown.extensions.command',
                          'moosedown.extensions.include'])



def command_line_options(subparser):
    build_parser = subparser.add_parser('build', help='Convert markdown into HTML or LaTeX.')
    #build_parser.add_argument('--extensions', nargs=?, help="The extensions")

# def load_config(filename):
#     """
#     Load and error check config file.
#     """
#
#     # Define defaults
#     config = mooseutils.yaml_load(filename)
#
#     #mod = importlib.import_module('moosedown.base.MarkdownReader')
#     #print mod
#
#     for opt in ['reader', 'renderer', 'translator']:
#         if isinstance(config[opt], str):
#             config[opt] = eval(config[opt])
#
#     return config

def params_to_dict(node):
    return {child.path():child.param() for child in node.children(node_type=hit.NodeType.Field)}


class ConfigException(Exception):
    pass


def load_extensions(node, errors=[]):
    """
    Instatiates the Extension objects, with the configuration from the hit file, for passing
    into the Translator object.

    Inputs:
        node[hit.Node|None]: The [Extensions] section of the hit file.
        errors[list]: A list for appending errors
    """

    # The key is the extension module name, value is a dict() of configuration options, which is populated
    # from the hit nodes and applied to the object via the make_extension method.
    if (node and node.param('disable_defaults')):
        ext_configs = dict()
    else:
        ext_configs = {k:dict() for k in DEFAULT_EXTENSIONS}

    # Process the [Extensions] block of the hit input, if it exists
    if node:
        # Update the extension conifigure options based on the content of the hit nodes
        for child in node.children(node_type=hit.NodeType.Section):
            ext_type = child.param('type') #TODO: accumulate error
            if ext_type is None:
                msg = "The section '{}' must contain a 'type' parameter.".format(child.fullpath())
                errors.append((msg, child.line()))
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
                errors.append("The supplied module '{}' must have a 'make_extension' function.".format(module.__name__))
            else:
                extensions.append(module.make_extension(**config))

        except ImportError as e:
            errors.append("Failed to import the '{}' module.".format(name))

    return extensions


def load_config(filename):

    # Read the config.hit file #TODO: error check on filename
    with open(filename) as f:
        content = f.read()
    root = hit.parse(filename, content)

    # Load extensions
    errors = []
    extensions = load_extensions(node.find('Extensions'), errors=errors)



    #print defaults
    #defaults = DEFAULT_EXTENSIONS.difference(ext.param('disable')) if












#    #TODO: error if Renderer not available
#    render_params = params_to_dict(root.find('Renderer'))




    #print render_params




    #node = root.find(settings['block'])
    #if node is not None:
    #    return node.render()





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
