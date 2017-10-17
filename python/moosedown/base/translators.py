import logging

from MooseDocs import common
LOG = logging.getLogger('Translator')

class Translator(object):

    @staticmethod
    def getConfig():
        return dict()

    def __init__(self, reader, renderer):
        self.__config = self.getConfig()
        self.__reader = reader
        self.__renderer = renderer
        self.__ast = None

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
