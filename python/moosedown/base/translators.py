import importlib
import logging
import inspect

from moosedown.tree import page
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

    def __init__(self, reader, renderer, extensions=[]):

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
        #self.__extensions = extensions
        #config, reader_extensions, render_extensions = self.load(extensions)
        self.__reader = reader
        self.__renderer = renderer
        self.__extensions = self.load(extensions)


        self.__reader.translator = self #TODO: init
        self.__renderer.translator = self #TODO: init

        for ext in self.__extensions:
            ext.init(self)
            ext.extend(reader, renderer)

        """
        for ext in reader_extensions:
            ext.init(self)
        for ext in render_extensions:
            ext.init(self)

        self.__config = self.getConfig()
        self.__config.update(config)
        #self.__config.update(kwargs)

        self.__reader = reader(reader_extensions)
        self.__reader.init(config)
        self.__renderer = renderer(render_extensions)
        self.__renderer.init(config)
        #self.__ast = None
        """

        self.__node = None

    def extensions(self):
        return self.__extensions

    @property
    def node(self):
        return self.__node

    def load(self, extensions):
        """
        Load the extensions and extension configure settings.
        """
        #config = dict()
        #reader_extensions = []
        ext_objects = []
        for ext in extensions:
            if isinstance(ext, str):
                module = importlib.import_module(ext)
            else:
                module = ext

            if not hasattr(module, 'make_extension'):
                msg = "The supplied module '{}' must have a 'make_extension' function."
                raise ImportError(msg.format(module.__name__))

            ext_objects.append(module.make_extension())

            """
            if reader_ext:
                if not isinstance(reader_ext, TokenExtension):
                    msg = "The first return item (reader object) returned by the {} extension must be " \
                          "an instance of a moosedown.base.TokenExtension, but a '{}' object was found."
                    raise TypeError(msg.format(module.__name__, type(reader_ext).__name__))
                config.update(reader_ext.getConfig())
                reader_extensions.append(reader_ext)

            if render_ext:
                if not isinstance(render_ext, RenderExtension):
                    msg = "The second return item (render object) returned by the {} extension must be "\
                          "an instance of a moosedown.base.RenderExtension, but a '{}' object was found."
                    raise TypeError(msg.format(module.__name__, type(render_ext).__name__))
                config.update(render_ext.getConfig())
                render_extensions.append(render_ext)
            """

        return ext_objects #config, reader_extensions, render_extensions


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

    def ast(self, content):
        #ast = self.__reader.parse(content)
        #print ast
        return self.__reader.parse(content)

    def convert(self, content):
        self.__node = content if isinstance(content, page.PageNodeBase) else None
        #self.__renderer.node = self.__node
        ast = self.ast(content)
        return ast, self.__renderer.render(ast)
