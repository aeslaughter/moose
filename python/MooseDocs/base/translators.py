"""
Module that defines Translator objects for converted AST from Reader to Rendered output from
Renderer objects. The Translator objects exist as a place to import extensions and bridge
between the reading and rendering content.
"""
import logging
import multiprocessing

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
        self._current = None

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
        return self._current

   # @property
   # def lock(self):
   #     return self.__lock


    #def init(self, pages): set the content...this cal call node.init(self)
    #    pass


    def reinit(self):
        """
        Reinitialize the Reader, Renderer, and all Extension objects.
        """
        tokens.CountToken.COUNTS.clear()
        self.reader.reinit()
        self.renderer.reinit()
        for ext in self.__extensions:
            ext.reinit()

    def ast(self, content):
        # TODO: content should loop over all nodes, in parallel...


        node = content if isinstance(content, page.PageNodeBase) else None
        self._current = node
        ast = tokens.Token(None)#, page=node) # root node
        self.reinit()
        if node:
            node.read()
            self.__reader.parse(ast, node.content)
        else:
            self.__reader.parse(ast, content)

        for ext in self.__extensions:
            ext.postTokenize(ast)

        self._current = None

        # TODO: cache current with ast as key

        return ast

    def render(self, ast):
        # TODO: content should loop over all nodes, in parallel...

        return self.__renderer.render(ast)

    #TODO: build() do parallel seld.ast then self.render

    """
    def convert(self, content):
        # Convert the supplied content by passing it into the Reader to build an AST. Then, the AST
        #is passed to the Renderer to create the desired output format.
        node = content if isinstance(content, page.PageNodeBase) else None
        ast = tokens.Token(None, page=node) # root node
        self.reinit()
        self.__reader.parse(ast, content)
        return ast, self.__renderer.render(ast)
    """
