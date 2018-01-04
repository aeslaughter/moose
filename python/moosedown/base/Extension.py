import logging

import moosedown
from moosedown import common
from ConfigObject import ConfigObject

LOG = logging.getLogger(__name__)

class Extension(ConfigObject):

    def __init__(self, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        self.__tranlator = None

    @property
    def translator(self):
        return self.__tranlator

    """
    @property
    def renderer(self):
        return self.translator.renderer

    @property
    def reader(self):
        return self.translator.reader
    """

    def init(self, translator):
        #TODO: error if called twice
        self.__tranlator = translator

    def reinit(self):
        pass

    def extend(self, reader, renderer):
        pass

    #def __iter__(self):
    #    for item in self.__items:
    #        yield item

"""
class ExtensionObject(ConfigObject):

    def __init__(self, extensions=[], **kwargs):
        ConfigObject.__init__(self, **kwargs)
        self.__extensions = extensions
        self.__initialized = False

    def add(self, *args, **kwargs):
        raise NotImplementedError("...") #TODO: improve this

    def init(self, **kwargs):
        #TODO: error if called again
        self.update(**kwargs)
        for ext in self.__extensions:
            ext.extend()
            for items in ext:
                self.add(*items)
        self.__initialized = True

    def reinit(self):
        for ext in self.__extensions:
            ext.reinit()

"""

"""
class RenderExtension(Extension): #TODO: inherit from Extension to get config stuff
    def __init__(self):
        Extension.__init__(self)
        self.__components = list()

    def reinit(self):
        for comp in self.__components:
            comp.reinit()


    def add(self, token_class, component):
        # TODO: test token_class is type
        component.init(self.translator)
        self.__components.append(component)
        func = component.renderer.method(component)
        Extension.add(self, token_class, func)

class TokenExtension(Extension):

    def __init__(self):
        Extension.__init__(self)
        self.__components = list()

    def reinit(self):
        for comp in self.__components:
            comp.reinit()


    def add(self, group, name, component, location='_end'):
        self.__components.append(component)
        component.init(self.translator)
        func = lambda m, p: self.__function(m, p, component)
        Extension.add(self, group, name, component.RE, func, location)

    def __function(self, match, parent, component):
        defaults = component.defaultSettings()
        if not isinstance(defaults, dict):
            raise common.exceptions.TokenizeException("The component '{}' must return a dict from the defaultSettings static method.".format(component))



        if 'settings' in match.groupdict() and component.PARSE_SETTINGS:
            component.settings, _ = common.parse_settings(defaults, match.group('settings'))
        else:
            component.settings = {k:v[0] for k, v in defaults.iteritems()}
        token = component.createToken(match, parent)
        return token

#class MarkdownExtension(TokenExtension):
"""
