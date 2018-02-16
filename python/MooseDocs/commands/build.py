"""
Defines the MooseDocs build command.
"""
import os
import copy
import logging
import importlib
import collections

import anytree
import livereload

import mooseutils

import moosedown
from moosedown import common

logging.basicConfig(level=logging.DEBUG) #TODO: need to get this into config
LOG = logging.getLogger(__name__)


def command_line_options(subparser):
    """
    Define the command line options for the build command.
    """
    build_parser = subparser.add_parser('build', help='Convert markdown into HTML or LaTeX.')
    build_parser.add_argument('--grammer', action='store_true',
                              help='Show the lexer components in order.')

def main(options):
    """
    Main function for the build command.
    """

    destination = os.path.join(os.getenv('HOME'), '.local', 'share', 'moose', 'site')
    logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.hit'

    # TODO: add this to config.hit and command line
    #LOG.setLevel(logging.DEBUG)

    translator, root = common.load_config(config_file)

    #TODO: clean this up with better format and make it a function
    if options.grammer:
        for key, grammer in translator.reader.lexer.grammers().iteritems():
            print 'GRAMMER:', key
            for pattern in grammer:
                print '  ', pattern

    if False:
        from moosedown.tree import page
        #filename = '/Users/slauae/projects/moosedown/docs/content/utilities/moosedown/autolink.md'
        filename = '/Users/slauae/projects/moosedown/docs/content/documentation/sqa/moose_sdd.md'
        node = page.MarkdownNode(source=filename)
        node.init(translator)
        node.read()
        ast = node.ast()
        html = node.render()
       # print ast
        #print html


    else:
        server = livereload.Server()
        for node in anytree.PreOrderIter(root):
            node.base = destination
            node.init(translator)# = translator

            if node.source and os.path.isfile(node.source):
                server.watch(node.source, node.build)


        # TODO: make these steps parallel, print progress (in parallel)
        # Breaking this up allows for the complete AST for all pages to be available to others
        # when rendering (see autolink.py)
        LOG.info("Building AST...")
        for node in anytree.PreOrderIter(root):
            if isinstance(node, moosedown.tree.page.MarkdownNode):
                node.ast()

        LOG.info("Rendering AST...")
        for node in anytree.PreOrderIter(root):
            if isinstance(node, moosedown.tree.page.MarkdownNode):
                node.render()


        for node in anytree.PreOrderIter(root):
            node.build(reset=False) #TODO: This probably should just be write()


        server.serve(root=destination, port=8000)
