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
        from MooseDocs.tree import page
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
            node.init(translator)# = translator

            if node.source and os.path.isfile(node.source):
                server.watch(node.source, node.build)

        # TODO: make these steps parallel, print progress (in parallel)
        # Breaking this up allows for the complete AST for all pages to be available to others
        # when rendering (see autolink.py)
        num_threads=multiprocessing.cpu_count()

        # TODO: move to translator ???
        nodes = [node for node in anytree.PreOrderIter(root) if isinstance(node, MooseDocs.tree.page.MarkdownNode)]

        LOG.info("Building AST...")
        for node in nodes:
            ast = node.ast()

        #import cProfile, pstats, StringIO
        #pr = cProfile.Profile()
        #pr.enable()

        LOG.info("Rendering AST...")
        for node in nodes:
            translator._current = node #TODO: figure out how to do this better
            node.render()
            translator._current = None

        #pr.disable()
        #s = StringIO.StringIO()
        #sortby = 'cumulative'
        #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        #ps.print_stats()
        #print s.getvalue()


        #manager = multiprocessing.Manager()
        #d = manager.dict()
        #q = multiprocessing.Queue()

        #import pickle
        #for node in nodes:
        #    ast = node.ast()
        #    print node.name
        #    pickle.dumps(ast)





        #import time
        #start = time.time()
        #for node in nodes:
        #    node.ast()
        #stop = time.time()
        #print 'AST: ', stop - start

        #runner = scheduler.Scheduler(num_threads=num_threads)
        #for node in nodes:
        #    runner.schedule(node.ast)
        #runner.waitFinish()


        """
        jobs = []
        for chunk in mooseutils.make_chunks(nodes, num_threads):
            p = multiprocessing.Process(target=build_ast, args=(d, chunk))
            p.start()
            jobs.append(p)

        for job in jobs:
            job.join()
        """


        #start = time.time()

        #for node in nodes:
        #    node.render()

        #runner = scheduler.Scheduler(num_threads=num_threads)
        #for node in nodes:
        #    runner.schedule(node.render)
        #runner.waitFinish()

        """
        jobs = []
        for chunk in mooseutils.make_chunks(nodes, num_threads):
            p = multiprocessing.Process(target=build_render, args=(chunk,))
            p.start()
            jobs.append(p)

        for job in jobs:
            job.join()
        """

       # stop = time.time()
       # print 'RENDER: ', stop - start


        #for node in anytree.PreOrderIter(root):
        #    if isinstance(node, MooseDocs.tree.page.MarkdownNode):
        #        node.ast()

        #for node in anytree.PreOrderIter(root):
        #    if isinstance(node, MooseDocs.tree.page.MarkdownNode):
        #        node.render()

        #for node in anytree.PreOrderIter(root):
        #    node.write()#reset=False) #TODO: This probably should just be write()

        #server.serve(root=destination, port=8000)

def build_ast(d, nodes):
    for node in nodes:
        ast = node.ast()
        #d[node.name] = ast

def build_render(nodes):
    for node in nodes:
        node.render()
