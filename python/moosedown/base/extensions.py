import logging

import moosedown
from moosedown import common

LOG = logging.getLogger(__name__)

class Extension(object):
    @staticmethod
    def getConfig():
        config = dict()
        return config

    def __init__(self):
        self.__config = dict()
        self.__items = list()
        self.__tranlator = None

    @property
    def translator(self):
        return self.__tranlator

    def update(self, config):
        self.__config.update(config)

    def init(self, translator):
        #TODO: error if called twice
        self.__tranlator = translator

    def reinit(self):
        pass

    def extend(self):
        pass

    def add(self, *args):
        self.__items.append(tuple(args))

    def __iter__(self):
        for item in self.__items:
            yield item

class RenderExtension(Extension): #TODO: inherit from Extension to get config stuff
    def __init__(self):
        Extension.__init__(self)
        self.__components = list()

    def reinit(self):
        for comp in self.__components:
            comp.reinit()

    @property
    def renderer(self):
        return self.translator.renderer

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

    @property
    def reader(self):
        return self.translator.reader

    def add(self, group, name, component, location='_end'):
        self.__components.append(component)
        component.init(self.translator)
        func = lambda m, p: self.__function(m, p, component)
        Extension.add(self, group, name, component.RE, func, location)

    def __function(self, match, parent, component):
        component.settings = {k:v[0] for k, v in component.defaultSettings().iteritems()}
        if 'settings' in match.groupdict() and component.PARSE_SETTINGS:
            component.settings, _ = common.parse_settings(component.settings, match.group('settings'))
        token = component.createToken(match, parent)
        return token


class MarkdownExtension(TokenExtension):
    #: Internal global for storing commands
    __COMMANDS__ = dict()

    def addCommand(self, command):
        command.init(self.translator)
        #TODO: error if it exists
        MarkdownExtension.__COMMANDS__[(command.COMMAND, command.SUBCOMMAND)] = command

    def addBlock(self, component, location='_end'):
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        super(MarkdownExtension, self).add(moosedown.BLOCK, name, component, location)

    def addInline(self, component, location='_end'):
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        super(MarkdownExtension, self).add(moosedown.INLINE, name, component, location)
