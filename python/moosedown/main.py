import logging
import base
#import common
#import extensions
logging.basicConfig()
def build():
    config = dict()
    config['materialize'] = (False, 'Enable the use of the Materialize framework for HTML output.')
    extensions = ['moosedown.extensions.core', 'moosedown.extensions.devel']
    #if ext is not None:
    #    extensions += ext

    #local = dict(commands=['extensions.command.CodeCompare'])
    #for key, value
    #for reader_ext, render_ext in zip(reader_extensions, render_extensions):
    #    reader_ext.update(config)
    #    render_ext.update(config)

    reader = base.MarkdownReader#(reader_extensions)

    #if config['materialize']:
    #    render = base.MaterializeRenderer#(render_extensions)
    #else:

    render = base.HTMLRenderer#(render_extensions)

    translator = base.Translator(reader, render, extensions, **config)

    with open('spec.md', 'r') as fid:
        md = fid.read()

    ast = translator.ast(md)
    print ast

    html = translator.convert()#'heading.md')
    #print html

    with open('index.html', 'w') as fid:
        fid.write(html.write())



def main():
    pass

if __name__ == '__main__':
    build()
