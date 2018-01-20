"""
Component objects are used for defining extensions for translating from
markdown to HTML/LaTeX.
"""
from moosedown.common import exceptions, parse_settings
from moosedown.tree import tokens
from lexers import LexerInformation
from translators import Translator


class Component(object):
    """
    Each extension is made up of components, both for tokenizing and rendering. The
    compoments provide a means for defining settings as well as other customizable
    features required for translation.
    """
    def __init__(self):
        self.__translator = None

    def init(self, translator):
        """
        Called by Translator object, this allows the Extension objects to be
        created independently then passed into the translator, which then
        calls this method to provide access to translator for when the actual
        tokenize and render commands are called.
        """
        if self.__translator is not None:
            msg = "The component has already been initialized, this method should not " \
                  "be called twice."
            raise exceptions.MooseDocsException(msg)

        if not isinstance(translator, Translator):
            msg = "The supplied object must be of type '{}', but a '{}' was provided."
            raise exceptions.MooseDocsException(msg, Translator, type(translator))

        self.__translator = translator

    @property
    def translator(self):
        """
        Returns the Translator object as property.
        """
        if self.__translator is None:
            msg = "Component object must be initialized prior to accessing this property."
            raise exceptions.MooseDocsException(msg)
        return self.__translator

    def reinit(self):
        """
        Called by the Translator prior to converting, this allows for state to be
        reset when using livereload.
        """
        pass

class TokenComponent(Component):
    """
    Base class for creating components designed to create token during tokenization.

    # Overview
    TokenComponent objects are designed to be created by Extension objects and added to the Reader
    object in the Extension:extend method. The purpose of a TokenComponent is to define a regular
    expresion, that when match returns a token that is added to the AST.

    The codebase of MooseDocs (Translator, Reader, Renderer) is certiainly capable of tokenizing
    arbitrary formats. However, the primary use case is for creating HTML so there are a certain
    features for this class that are setup with that application in mind.

    ## RE Class Member
    The RE class member variable is used for convience to
    allow for derived classes to avoid creating an __init__ method. As shown in core.py the purpose
    of this class is to be able to add parser syntax for tokenizing with a minimal amount code, the
    following static member variables aid in the design goal.

    RE must be defined as a compile re expresion that captures the content to be converted to a
    token within the createToken method.  - TOKEN: The token type (not instance) that will be
    created

    ## Settings
    If the supplied regex match option has a group named "settings" these settings will be
    automatically parsed by the translator and used to update the values returned by the
    defaultSettings method. These settings must be key-value pairings that use an equal sign that is
    does not contains spaces on either side (e.g., foo=bar).

    The automatic parsing settings may be disable by setting the PARSE_SETTINGS class member
    variable to False in the child object.
    """
    RE = None
    PARSE_SETTINGS = True

    @staticmethod
    def defaultSettings():
        """
        Default settings for the compomenent. Child classes should define a similar method to create
        the default settings for the compoment, see core.py for examples.
        """
        settings = dict()
        settings['style'] = (u'', "The style settings that are passed to the HTML flags.")
        settings['class'] = (u'', "The class settings to be passed to the HTML flags.")
        settings['id'] = (u'', "The class settings to be passed to the HTML flags.")
        return settings

    def __init__(self):
        """
        Constructs the object and sets the default settings of the object.
        """
        Component.__init__(self)

        # Local settings, this is updated by the Reader just prior to calling the createToken()
        self.__settings = dict()


    def __call__(self, info, parent):
        """
        MooseDocs internal method, this should not be called, please use the createToken method.

        The lexer system within MooseDocs expects a function this method allows this class to act
        as a function.

        Inputs:
            info[LexerInformation]: Object containing the lexer information object.
            parent[tokens.Token]: The parent node in the AST for the token being created.
        """
        if not isinstance(info, LexerInformation):
            msg = "The 'info' input must be a {} object, but a {} was provided."
            raise common.exceptions.TokenizeException(msg, LexerInformation, type(info))

        if not isinstance(parent, tokens.Token):
            msg = "The 'parent' input must be a {} object, but a {} was provided."
            raise common.exceptions.TokenizeException(msg, tokens.Token, type(parent))

        defaults = self.defaultSettings()
        if not isinstance(defaults, dict):
            msg = "The component '{}' must return a dict from the defaultSettings static method."
            raise common.exceptions.TokenizeException(msg, self)

        if 'settings' in match and self.PARSE_SETTINGS:
            self.__settings, _ = parse_settings(defaults, match['settings'])
        else:
            self.__settings = {k:v[0] for k, v in defaults.iteritems()}
        return self.createToken(match, parent)

    @property
    def attributes(self):
        """
        Return a dictionary with the common html settings.
        """
        return {'style':self.settings['style'], 'id':self.settings['id'], 'class':self.settings['class']}

    @property
    def settings(self):
        """
        Retrun a copy of the settings, without the setting descriptions.
        """
        return self.__settings

    @property
    def reader(self):
        """
        Return the Reader object.
        """
        return self.translator.reader

    def createToken(self, info, parent):
        """
        Method designed to be implemented by child classes, this method should create the
        token for the AST based on the regex match.

        Inputs:
            info[LexerInformation]: Object containing the lexer information object.
            parent[tokens.Token]: The parent node in the AST for the token being created.
        """
        raise NotImplementedError("The createToken method is required.")

class RenderComponent(Component):

    def __init__(self):
        Component.__init__(self)

    @property
    def renderer(self):
        return self.translator.renderer
