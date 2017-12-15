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

    def update(self, config):
        self.__config.update(config)

    def setup(self, *args, **kwargs):
        pass

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
        self.__renderer = None
        self.__components = list()

    def reinit(self):
        for comp in self.__components:
            comp.reinit()

    @property
    def renderer(self):
        return self.__renderer

    """
    @renderer.setter
    def renderer(self, value):
        #TODO: type check
        self.__renderer = value
    """

    def setup(self, renderer):
        #TODO: type and error check
        self.__renderer = renderer

    def add(self, token_class, component):
        # TODO: test token_class is type
        component.setup(self.__renderer)
        self.__components.append(component)
        func = component.renderer.method(component)
        Extension.add(self, token_class, func)

class TokenExtension(Extension):

    def __init__(self):
        Extension.__init__(self)
        self.__reader = None
        self.__components = list()

    def reinit(self):
        for comp in self.__components:
            comp.reinit()

    def setup(self, reader):
        #TODO: type check
        self.__reader = reader

    @property
    def reader(self):
        return self.__reader

    def add(self, group, name, component, location='_end'):
        self.__components.append(component)
        component.setup(self.__reader)
        func = lambda m, p: self.__function(m, p, component)
        Extension.add(self, group, name, component.RE, func, location)

    def __function(self, match, parent, component):
        component.settings = component.defaultSettings()
        if 'settings' in match.groupdict() and component.PARSE_SETTINGS:
            component.settings, _ = common.parse_settings(component.settings, match.group('settings'))
        token = component.createToken(match, parent)
        return token


class MarkdownExtension(TokenExtension):
    #: Internal global for storing commands
    __COMMANDS__ = dict()
    __BLOCKCOMMANDS__ = dict()

    def addCommand(self, command):
        command.setup(self.reader)
        #TODO: error if it exists
        MarkdownExtension.__COMMANDS__[(command.COMMAND, command.SUBCOMMAND)] = command

    """
    def addBlockCommand(self, command):
        command.setup(self.reader)
        MarkdownExtension.__BLOCKCOMMANDS__[(command.COMMAND, command.SUBCOMMAND)] = command
    """

    def addBlock(self, component, location='_end'):
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        super(MarkdownExtension, self).add(moosedown.BLOCK, name, component, location)

    def addInline(self, component, location='_end'):
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        super(MarkdownExtension, self).add(moosedown.INLINE, name, component, location)
