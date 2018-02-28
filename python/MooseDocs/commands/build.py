"""
Defines the MooseDocs build command.
"""
import os
import copy
import logging
import importlib
import collections
import multiprocessing
import shutil

import anytree
import livereload

import mooseutils
import scheduler

import MooseDocs
from MooseDocs import common
from MooseDocs.tree import page


def command_line_options(subparser, parent):
    """
    Define the command line options for the build command.
    """
    build_parser = subparser.add_parser('build',
                                        parents=[parent],
                                        help='Convert markdown into HTML or LaTeX.')
    build_parser.add_argument('--grammer', action='store_true',
                              help='Show the lexer components in order.')
    return build_parser

def main(options):
    """
    Main function for the build command.
    """
    LOG = logging.getLogger('MooseDocs.build')

    destination = os.path.join(os.getenv('HOME'), '.local', 'share', 'moose', 'site')

    if os.path.exists(destination):
        shutil.rmtree(destination)

    #logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.yml'

    # TODO: add this to config.hit and command line
    #LOG.setLevel(logging.DEBUG)

    translator, root = common.load_config(config_file)
    #print root

    #TODO: clean this up with better format and make it a function
    if options.grammer:
        for key, grammer in translator.reader.lexer.grammers().iteritems():
            print 'GRAMMER:', key
            for pattern in grammer:
                print '  ', pattern

    if False:
        #from MooseDocs.tree import page
        #filename = '/Users/slauae/projects/moosedown/docs/content/utilities/MooseDocs/autolink.md'
        #filename = '/Users/slauae/projects/MooseDocs/docs/content/documentation/sqa/moose_sdd.md'
        filename = '/Users/slauae/projects/moosedown/framework/doc/content/documentation/systems/Adaptivity/Markers/ValueRangeMarker.md'
        node = page.MarkdownNode(source=filename)
        node.init(translator)
        node.read()
        ast = node.ast()
        html = node.render()
        print ast
        #print html


    else:
        server = livereload.Server()
        for node in anytree.PreOrderIter(root):
            node.base = destination
            if node.source and os.path.isfile(node.source):
                server.watch(node.source, node.build)

        num_threads=multiprocessing.cpu_count()

        # TODO: Talk about multiprocessing limitations

        translator.init(root)
        translator.tokenize(num_threads=num_threads)

        # "write" all nodes, this creates the directories
        translator.write(num_threads=num_threads)

        translator.render(num_threads=num_threads)


        server.serve(root=destination, port=8000)
