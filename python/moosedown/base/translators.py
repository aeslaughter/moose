import importlib
import logging

from MooseDocs import common
LOG = logging.getLogger('Translator')

class Translator(object):

    @staticmethod
    def getConfig():
        config = dict()
        #config['extensions'] = ([], "List of extensions to load.")
        #config['reader'] = ('base.MarkdownReader', "The reader.")
        #config['renderer'] = ('base.MarkdownReader', "The reader.")

        return config

    def __init__(self, reader, renderer, extensions=[], **kwargs):
        #TODO: error check on types

        config, reader_extensions, render_extensions = self.load(extensions)



        self.__config = self.getConfig()
        self.__config.update(config)
        self.__config.update(kwargs)

        self.__reader = reader(reader_extensions)
        self.__renderer = renderer(render_extensions)
        self.__ast = None

    def load(self, extensions):
        """
        """
        config = dict()
        reader_extensions = []
        render_extensions = []
        for ext in extensions:
            if isinstance(ext, str):
                module = importlib.import_module(ext)
            else:
                module = ext

            #TODO: test for 'make_extension'
            reader_ext, render_ext = module.make_extension()
            #TODO: check return types

            config.update(reader_ext.getConfig())
            config.update(render_ext.getConfig())

            reader_extensions.append(reader_ext)
            render_extensions.append(render_ext)
        return config, reader_extensions, render_extensions


    @property
    def reader(self):
        #TODO: Error check
        return self.__reader

    @property
    def renderer(self):
        #TODO: Error check
        return self.__renderer

    def ast(self, filename):
        self.__ast = self.__reader.parse(filename)
        return self.__ast

    def convert(self, filename=None):
        if self.__ast is None:
            self.ast(filename)
        if self.__ast is None and filename is None:
            raise Exception('don not do this') #TODO: make more better
        return self.__renderer.render(self.__ast)
