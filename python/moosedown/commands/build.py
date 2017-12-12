import os
import copy
import shutil
import mooseutils
import anytree
import livereload
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

    destination = '/Users/slauae/.local/share/moose/site'
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    else:
        os.makedirs(destination)

    config_file = 'config.yml'


    data = load_config(config_file)
    root = moosedown.tree.build_page_tree.doc_tree(data['pages'].values())
    translator = data['translator'](data['reader'], data['renderer'], data['extensions'])


    server = livereload.Server()

    root.name = '' #TODO: This should not be needed
    for node in anytree.PreOrderIter(root):
        if isinstance(node, moosedown.tree.page.MarkdownNode):
            node.function = translator.convert

        node.root = destination
        node.write()

        if node.source and os.path.isfile(node.source):
            print 'WATCH:', node.source
            server.watch(node.source, node.write)


    server.serve(root=destination, port=8000)
