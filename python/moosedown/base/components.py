from translators import Translator

class Component(object):
    RE = None
    TOKEN = None
    PARSE_SETTINGS = True

    @staticmethod
    def defaultSettings():
        return dict()

    def __init__(self):
        self.__settings = dict()
    #    self.__line = None
        self.__config = dict()
        self.__tranlator = None

    """
    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, config):
        self.__config = config
    """

    def init(self, translator):
        #TODO: error if called twice
        if not isinstance(translator, Translator):
            raise TypeError("The supplied object must be of type 'Translator', but a '{}' was provided.".format(type(translator).__name__))
        #TODO: type and error check
        self.__tranlator = translator

    @property
    def translator(self):
        return self.__tranlator


    """
    @property
    def line(self):
        return self.__line

    @line.setter
    def line(self, value):
        self.__line = value
    """

#    def reinit(self):
#        pass

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, values):
        self.__settings = values

class TokenComponent(Component):

    def __init__(self):
        Component.__init__(self)

    @property
    def reader(self):
        return self.translator.reader

    def createToken(self, match, parent):
        pass

class RenderComponent(Component):

    def __init__(self):
        Component.__init__(self)

    @property
    def renderer(self):
        return self.translator.renderer
