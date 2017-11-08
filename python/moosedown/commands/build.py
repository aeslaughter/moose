import re

from moosedown import base
from moosedown import tree

def command_line_options(subparser):
    build_parser = subparser.add_parser('build', help='Convert markdown into HTML or LaTeX.')
    #build_parser.add_argument('--extensions', nargs=?, help="The extensions")


def main():
    config = dict()
    config['materialize'] = (False, 'Enable the use of the Materialize framework for HTML output.')
    extensions = ['moosedown.extensions.core', 'moosedown.extensions.devel']
    reader = base.MarkdownReader
    render = base.LatexRenderer

    #render = base.MaterializeRenderer
    #render = base.HTMLRenderer

    translator = base.Translator(reader, render, extensions, **config)

    #node = tree.file.FileNode(source='spec.md')


    with open('spec.md', 'r') as fid:
        md = fid.read()


    ast = translator.ast(md)
   # print ast

    html = translator.convert()
    print html


    with open('index.tex', 'w') as fid:

        fid.write(re.sub(r'\n+', r'\n', html.write()))

   # with open('index.html', 'w') as fid:
    #    fid.write(html.write())
