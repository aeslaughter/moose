import os
import importlib
import logging
import inspect

from moosedown.tree import tokens, page #TODO: change to pages
from lexers import LexerInformation #TODO: make this MetaData or something better and move from lexer
from readers import Reader
from renderers import Renderer
from extensions import Extension
from ConfigObject import ConfigObject
LOG = logging.getLogger('Translator')

class Translator(ConfigObject):
    """
    Object responsible for converting reader content into an AST and rendering with the
    supplied renderer.

    Inputs:
        reader: [type] A Reader class (not instance).
        renderer: [type] A Renderer class (not instance).
        extensions: [list] A list of extensions objects to use.
    """


    def __init__(self, reader, renderer, extensions=[], debug=False, **kwargs):
        ConfigObject.__init__(self, **kwargs)

        # Check that supplied reader/renderr are types
        #if not isinstance(reader, type):
        #    msg = "The supplied reader must be a 'type' but {} was provided."
        #    raise TypeError(msg.format(type(reader).__name__))

        #if not isinstance(renderer, type):
        #    msg = "The supplied renderer must be a 'type' but {} was provided."
        #    raise TypeError(msg.format(type(renderer).__name__))

        # Check inheritence
        #if Reader not in inspect.getmro(reader):
        #    raise TypeError("The supplied reader must inherit from moosedown.base.Reader.")

        #if Renderer not in inspect.getmro(renderer):
        #    raise TypeError("The supplied renderer must inherit from moosedown.base.Renderer.")


        # Load the extensions
        self.__extensions = extensions
        #config, reader_extensions, render_extensions = self.load(extensions)
        self.__reader = reader
        self.__renderer = renderer

        self.__reader.translator = self #TODO: self.__reader.init(self)
        self.__renderer.translator = self #TODO: init

        for ext in self.__extensions:
            ext.init(self)
            ext.extend(reader, renderer)

        #self.__node = None

    @property
    def extensions(self):
        return self.__extensions

    #@property
    #def node(self):
    #  return self.__node

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
        #self.reinit()
        #self.__renderer.node = self.__node
        self.__reader.parse(ast, content)
    #    print ast
        return ast, self.__renderer.render(ast)
