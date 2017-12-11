from MooseDocs import common

class Component(object):
    RE = None
    TOKEN = None

    @staticmethod
    def defaultSettings():
        return dict()

    def __init__(self):
        self.__settings = dict()
        self.__line = None
        self.__config = dict()

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, config):
        self.__config = config

    @property
    def line(self):
        return self.__line

    @line.setter
    def line(self, value):
        self.__line = value

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, values):
        self.__settings = values

    def error(self, *args):
        #TODO: This should report the line number of the error
        print 'ERROR: ' + ' '.join(args)

class TokenComponent(Component):

    def __init__(self):
        Component.__init__(self)
        self.__reader = None

    @property
    def reader(self):
        return self.__reader

    @reader.setter
    def reader(self, value):
        #TODO: type check
        self.__reader = value

    def createToken(self, match, parent):
        pass

class RenderComponent(Component):

    def __init__(self):
        Component.__init__(self)
        self.__renderer = None #TODO: only for RenderComponent

    @property
    def renderer(self):
        return self.__renderer

    @renderer.setter
    def renderer(self, value):
        #TODO: type check
        self.__renderer = value

class CommandComponent(TokenComponent):
    COMMAND = None#'devel'
    SUBCOMMAND = None#'moosedown'
