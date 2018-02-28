"""
Module that defines Translator objects for converted AST from Reader to Rendered output from
Renderer objects. The Translator objects exist as a place to import extensions and bridge
between the reading and rendering content.
"""
import logging
import multiprocessing
import codecs

import anytree

import mooseutils

import MooseDocs
from MooseDocs import common
from MooseDocs.common import mixins
from MooseDocs.tree import tokens, page
from readers import Reader
from renderers import Renderer

LOG = logging.getLogger('Translator')

class Translator(mixins.ConfigObject):
    """
    Object responsible for converting reader content into an AST and rendering with the
    supplied renderer.

    Inputs:
        reader: [Reader] A Reader instance.
        renderer: [Renderer] A Renderer instance.
        extensions: [list] A list of extensions objects to use.
    """
    def __init__(self, reader, renderer, extensions=None, **kwargs):
        mixins.ConfigObject.__init__(self, **kwargs)

        if extensions is None:
            extensions = []

        common.check_type('reader', reader, Reader)
        common.check_type('renderer', renderer, Renderer)
        common.check_type('extensions', extensions, list)

        #self.__lock = multiprocessing.Lock()

        self.__extensions = extensions
        self.__reader = reader
        self.__renderer = renderer

        self.__root = None
        self.__nodes = None
        self.__current = None
        self.__ast_cache = dict()

        self.__reader.init(self)
        self.__renderer.init(self)

        for ext in self.__extensions:
            common.check_type('extensions', ext, MooseDocs.base.components.Extension)
            ext.init(self)
            ext.extend(reader, renderer)
            for comp in self.__reader.components:
                if comp.extension is None:
                    comp.extension = ext
            for comp in self.__renderer.components:
                if comp.extension is None:
                    comp.extension = ext

    @property
    def extensions(self):
        """
        Return list of loaded Extension objects.
        """
        return self.__extensions

    @property
    def reader(self):
        """
        Return the Reader object.
        """
        return self.__reader

    @property
    def renderer(self):
        """
        Return the Renderer object.
        """
        return self.__renderer

    @property
    def current(self):
        return self.__current

   # @property
   # def lock(self):
   #     return self.__lock


    def init(self, pages):
        common.check_type('pages', pages, page.PageNodeBase)
        self.__root = pages

        self.__nodes = []
        for node in anytree.PreOrderIter(self.__root):
            if isinstance(node, page.MarkdownNode):
                node.init(self)
                self.__nodes.append(node)

    def reinit(self):
        """
        Reinitialize the Reader, Renderer, and all Extension objects.
        """
        tokens.CountToken.COUNTS.clear()
        self.reader.reinit()
        self.renderer.reinit()

        for node in self.__nodes:
            node.reinit()

        for ext in self.__extensions:
            ext.reinit()

    def ast(self, node):
        return self.__ast_cache[node.source]

    def tokenize(self, num_threads=1):
        """Build AST for all pages."""

        LOG.info("Building AST...")

        self.reinit()
        for node in self.__nodes:
            LOG.debug("Tokenize %s", node.source)
            self.__tokenize(node)
            self.__current = None

    def render(self, num_threads=1):
        """Convert all pages to HTML."""
        LOG.info("Rendering AST...")

        def target(nodes):
            for node in nodes:
                self.__render(node)

        jobs = []
        for chunk in mooseutils.make_chunks(self.__nodes, num_threads):
            p = multiprocessing.Process(target=target, args=(chunk,))
            p.start()
            jobs.append(p)

        for job in jobs:
            job.join()


        #for node in self.__nodes:
        #    LOG.debug("Render %s", node.source)
        #    self.__current = node
        #    self.renderer.render(self.__ast_cache[node])
        #    self.__current = None

    def build(self, node):
        LOG.info("Building %s", node.source)
        if MooseDocs.LOG_LEVEL == logging.DEBUG:
            common.check_type('node', node, page.MarkdownNode)

        self.__tokenize(node)
        self.__render(node)

    def __tokenize(self, node):
        self.__current = node
        ast = tokens.Token(None)
        self.reader.parse(ast, node.content)
        for ext in self.__extensions:
            ext.postTokenize(ast)
        self.__current = None
        self.__ast_cache[node.source] = ast

    def __render(self, node):
        self.__current = node
        html = self.renderer.render(self.__ast_cache[node.source])

        #TODO: this should be separate write method, but need to get html pickling
        dst = node.destination
        LOG.debug('Writing %s -> %s', node.source, dst)
        with codecs.open(dst, 'w', encoding='utf-8') as fid:
            fid.write(html.write())


        self.__current = None
