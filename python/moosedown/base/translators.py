"""
Module that defines Translator objects for converted AST from Reader to Rendered output from
Renderer objects. The Translator objects exist as a place to import extensions and bridge
between the reading and rendering content.
"""
import logging

import moosedown
from moosedown import common
from moosedown.tree import tokens, page
from readers import Reader
from renderers import Renderer
from __internal__ import ConfigObject

LOG = logging.getLogger('Translator')

class Translator(ConfigObject):
    """
    Object responsible for converting reader content into an AST and rendering with the
    supplied renderer.

    Inputs:
        reader: [Reader] A Reader instance.
        renderer: [Renderer] A Renderer instance.
        extensions: [list] A list of extensions objects to use.
    """
    def __init__(self, reader, renderer, extensions=None, **kwargs):
        ConfigObject.__init__(self, **kwargs)

        if extensions is None:
            extensions = []

        common.check_type('reader', reader, Reader)
        common.check_type('renderer', renderer, Renderer)
        common.check_type('extensions', extensions, list)

        self.__extensions = extensions
        self.__reader = reader
        self.__renderer = renderer

        self.__reader.init(self)
        self.__renderer.init(self)

        for ext in self.__extensions:
            common.check_type('extensions', ext, moosedown.base.components.Extension)
            ext.init(self)
            ext.extend(reader, renderer)

    @property
    def extensions(self):
        """
        Return list of loaded Extension objects.
        """
        return self.__extensions

    def reinit(self):
        """
        Reinitializes the Reader, Renderer, and all Extension objects.
        """
        self.reader.reinit()
        self.renderer.reinit()
        for ext in self.__extensions:
            ext.reinit()

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

    def convert(self, content):
        """
        Convert the supplied content by passing it into the Reader to build an AST. Then, the AST
        is passed to the Renderer to create the desired output format.
        """
        node = content if isinstance(content, page.PageNodeBase) else None
        ast = tokens.Token(None, page=node) # root node
        self.reinit()
        self.__reader.parse(ast, content)
        return ast, self.__renderer.render(ast)
