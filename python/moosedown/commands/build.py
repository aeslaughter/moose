import os
import copy
import shutil
import logging
import anytree
import livereload

import mooseutils


import moosedown

def command_line_options(subparser):
    build_parser = subparser.add_parser('build', help='Convert markdown into HTML or LaTeX.')
    #build_parser.add_argument('--extensions', nargs=?, help="The extensions")

def load_config(filename):
    """
    Load and error check config file.
    """

    # Define defaults




    config = mooseutils.yaml_load(filename)

    #mod = importlib.import_module('moosedown.base.MarkdownReader')
    #print mod

    for opt in ['reader', 'renderer', 'translator']:
        if isinstance(config[opt], str):
            config[opt] = eval(config[opt])




    return config

def main():
    #config = dict()
    #config['materialize'] = (False, 'Enable the use of the Materialize framework for HTML output.')
    #extensions = ['moosedown.extensions.core', 'moosedown.extensions.devel']

    #logging.basicConfig(level=logging.DEBUG)

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
