"""
Component objects are used for defining extensions for translating from
markdown to HTML/LaTeX.
"""
from translators import Translator

class Component(object):
    """
    Each extension is made up of components, both for tokenizing and rendering. The
    compoments provide a means for defining settings as well as other customizable
    features required for translation.
    """
    def __init__(self):
        super(Component, self).__init__
        self.__translator = None

    def init(self, translator):
        """
        Called by Translator object, this allows the Extension objects to be
        created independently then passed into the translator, which then
        calls this method to provide access to translator for when the actual
        tokenize and render commands are called.
        """
        #TODO: error if called twice
        if not isinstance(translator, Translator):
            raise TypeError("The supplied object must be of type 'Translator', but a '{}' was provided.".format(type(translator).__name__))
        #TODO: type and error check
        self.__translator = translator

    @property
    def translator(self):
        """
        Returns the Translator object as property.
        """
        if self.__translator is None:
            raise Exception("Foo")
        #TODO: raise if None
        return self.__translator

    def reinit(self):
        """
        Called by the Translator prior to converting, this allows for state to be
        reset when using livereload.
        """
        pass


class TokenComponent(Component):
    RE = None
    TOKEN = None
    PARSE_SETTINGS = True

    @staticmethod
    def defaultSettings():
        return dict()


    def __init__(self):
        Component.__init__(self)
        self.__settings = dict()

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, values):
        self.__settings = values


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
