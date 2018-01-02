import copy
import anytree
import textwrap
import logging

import moosedown

from moosedown.tree import tokens, page
from lexers import RecursiveLexer

from ReaderRenderBase import ReaderRenderBase

LOG = logging.getLogger(__name__)

class Reader(ReaderRenderBase):

    def __init__(self, lexer, extensions=None):
        self.__lexer = lexer
        #self.__node = None
        #self.__old_node = None
        ReaderRenderBase.__init__(self, extensions)

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

    def add(self, *args):#name, regex, func, location=-1):
        print args
        self.__lexer.add(*args)

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
    def __init__(self, ext=None):
        super(MarkdownReader, self).__init__(lexer=RecursiveLexer(moosedown.BLOCK, moosedown.INLINE),
                                             extensions=ext)
