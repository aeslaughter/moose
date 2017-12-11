import os
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


    root.name = '' #TODO: This should not be needed

    for node in anytree.PreOrderIter(root):
        if isinstance(node, moosedown.tree.page.MarkdownNode):
            node.function = translator.convert
        node.write(destination)


    #server = livereload.Server()
    #server.serve(root=os.path.join(destination, 'utilities', 'moosedown'))
        #if isinstance(node, moosedown

        #print node.local

            #print html



    #reader = base.MarkdownReader
    #render = base.LatexRenderer
    #render = base.MaterializeRenderer
    #render = base.HTMLRenderer

    #translator = base.Translator(reader, render, extensions, **config)

    #node = tree.file.FileNode(source='spec.md')


    #with open('spec.md', 'r') as fid:
    #    md = fid.read()


    #ast = translator.ast(md)
    #print ast

   # html = translator.convert()
#    print html


    #with open('index.tex', 'w') as fid:

     #   fid.write(re.sub(r'\n+', r'\n', html.write()))

   # with open('index.html', 'w') as fid:
    #    fid.write(html.write())
