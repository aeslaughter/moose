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

    def parse(self, root, content):

        if not isinstance(root, tokens.Token):
            raise TypeError("Wrong type...") #TODO

        self.reinit()

        #ast = root if root else tokens.Token(None)
        #self.__old_node = self.__node

        node = page.PageNodeBase(content=content) if isinstance(content, unicode) else content
        if not isinstance(node, page.PageNodeBase):
            raise TypeError("The supplied content must be a unicode or PageNodeBase object, but {} was provided.".format(type(node)))

        self.__lexer.tokenize(root, self.__lexer.grammer(), node.content)

        for token in anytree.PreOrderIter(root):
            if isinstance(token, tokens.Exception):
                self._exceptionHandler(token)


    def add(self, group, name, component, location='_end'):
        #TODO: check type must be TokenComponent

        self.__components.append(component)
        component.init(self.translator)
        self.__lexer.add(group, name, component.RE, component, location)


    @staticmethod
    def _exceptionHandler(token):
        n = 100
        title = []
        if isinstance(token.root.page, page.LocationNodeBase):
            title += textwrap.wrap(u"An exception occurred while tokenizing, the exception was " \
                                   u"raised when executing the {} object while processing the " \
                                   u"following content.".format(token.info.pattern.name), n)
            title += [u"{}:{}".format(token.root.page.source, token.info.line)]
        else:
            title += textwrap.wrap(u"An exception occurred on line {} while tokenizing, the " \
                                   u"exception was raised when executing the {} object while " \
                                   u"processing the following content." \
                                   .format(token.info.line, token.info.pattern.name), n)

        box = moosedown.common.box(token.info[0], line=token.info.line, width=n)
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
