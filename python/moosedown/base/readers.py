import copy
import anytree
import textwrap
import logging

import moosedown

from moosedown import common
from moosedown.tree import tokens, page
from lexers import RecursiveLexer
from ConfigObject import ConfigObject

LOG = logging.getLogger(__name__)

class Reader(ConfigObject):

    def __init__(self, lexer, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        self.__lexer = lexer
        self.__components = []
        #self.__node = None
        #self.__old_node = None
        #ExtensionObject.__init__(self, extensions, **kwargs)

        self.translator = None

    def reinit(self):
        for comp in self.__components:
            comp.reinit()

    @property
    def lexer(self):
        return self.__lexer

    #@property
    #def node(self):
    #    return self.__node

    """
    def read(self, input):
        with open(filename, 'r') as fid:
            text = fid.read()
        return self.parse(text)
    """

    def parse(self, node, root=None):
        self.reinit()

        ast = root if root else tokens.Token(None)
        #self.__old_node = self.__node


        if isinstance(node, unicode):
            node = page.PageNodeBase(content=node)

        if not isinstance(node, page.PageNodeBase):
            raise TypeError("The supplied content must be a unicode or PageNodeBase object.")

        self.__lexer.tokenize(node.content, ast, node=node)

        for token in anytree.PreOrderIter(ast):
            if isinstance(token, tokens.Exception):
                self._exceptionHandler(token, node)

        #self.__node = self.__old_node
        return ast


    def add(self, group, name, component, location='_end'):
        self.__components.append(component)
        component.init(self.translator)
        func = lambda m, p: self.__function(m, p, component)
        self.__lexer.add(group, name, component.RE, func, location)

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


#    def add(self, *args):#name, regex, func, location=-1):
#        self.__lexer.add(*args)




    @staticmethod
    def _exceptionHandler(token, node):
        n = 100
        title = []
        if isinstance(node, page.LocationNodeBase):
            token.source = node.source
            title += textwrap.wrap(u"An exception occurred while tokenizing, the exception was " \
                                   u"raised when executing the {} object while processing the " \
                                   u"following content.".format(token.pattern.name), n)
            title += [u"{}:{}".format(node.source, token.line)]
        else:
            title += textwrap.wrap(u"An exception occurred on line {} while tokenizing, the " \
                                   u"exception was raised when executing the {} object while " \
                                   u"processing the following content." \
                                   .format(token.line, token.pattern.name), n)

        box = moosedown.common.box(token.match.group(0), line=token.line, width=n)
        LOG.exception(u'\n{}\n{}\n{}\n\n'.format(u'\n'.join(title), box, token.traceback))


class MarkdownReader(Reader):
    def __init__(self, **kwargs):
        Reader.__init__(self,
                        lexer=RecursiveLexer(moosedown.BLOCK, moosedown.INLINE),
                        **kwargs)
        self._commands = dict()

    def addCommand(self, command):
        # TODO: All Command related stuff is in the command extensions, with the exception of
        # this function. Figure out how to avoid this special code here...
        command.init(self.translator)
        #TODO: error if it exists
        self._commands[(command.COMMAND, command.SUBCOMMAND)] = command

    def addBlock(self, component, location='_end'):
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        Reader.add(self, moosedown.BLOCK, name, component, location)

    def addInline(self, component, location='_end'):
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        Reader.add(self, moosedown.INLINE, name, component, location)
