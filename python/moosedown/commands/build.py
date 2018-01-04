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


def load_extensions(root):
    errors = []

    node = root.find('Extensions')
    if node is None:
        pass #TODO: accumulate errors and report all at end DO NOTHING and use defaults

    # Determine the list of defaults to build
    disable = node.param('disable').split()
    if disable:
        defaults = DEFAULT_EXTENSIONS.difference(set(disable))
    else:
        defaults = DEFAULT_EXTENSIONS

    ext_configs = dict()
    for ext in defaults:
        ext_configs[ext] = dict()

    # Build defaults
    #extensions = dict()
    #for name in defaults:
    #    extensions[name] = eval(name) #TODO: accumulate error if it fails

    # Build/update the extensions from config file
    for child in node.children(node_type=hit.NodeType.Section):
        ext_type = child.param('type') #TODO: accumulate error

        config = params_to_dict(child)
        config.pop('type')
        ext_configs[ext_type] = config


    extensions = []
    for name, config in ext_configs.iteritems():
        module = importlib.import_module(name)

        if not hasattr(module, 'make_extension'):
            msg = "The supplied module '{}' must have a 'make_extension' function."
            #raise ImportError(msg.format(module.__name__)) TODO: accumulate errors

        else:
            extensions.append(module.make_extension(**config))


    return extensions, errors


def load_config(filename):

    # Read the config.hit file #TODO: error check on filename
    with open(filename) as f:
        content = f.read()
    root = hit.parse(filename, content)

    # EXTENSIONS
    extensions = load_extensions(roots)



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
