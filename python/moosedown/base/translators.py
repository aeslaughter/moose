import os
import importlib
import logging
import inspect

import moosedown
from moosedown import common
from moosedown.tree import tokens, page #TODO: change to pages
from lexers import LexerInformation #TODO: make this MetaData or something better and move from lexer
from readers import Reader
from renderers import Renderer
#from components import Extension
from ConfigObject import ConfigObject
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
    def __init__(self, reader, renderer, extensions=[], debug=False, **kwargs):
        ConfigObject.__init__(self, **kwargs)

        common.check_type('reader', reader, Reader)
        common.check_type('renderer', renderer, Renderer)
        common.check_type('extensions', extensions, list)

        # Load the extensions
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
        return self.__extensions

    def reinit(self):
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
        node = content if isinstance(content, page.PageNodeBase) else None
        ast = tokens.Token(None, page=node) # root node
        self.reinit()
        self.__reader.parse(ast, content)
        return ast, self.__renderer.render(ast)
