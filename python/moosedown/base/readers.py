import copy
import moosedown
from moosedown.tree import tokens, page
from lexers import RecursiveLexer

from ReaderRenderBase import ReaderRenderBase

class Reader(ReaderRenderBase):

    def __init__(self, lexer, extensions=None):
        self.__lexer = lexer
#        self.__node = None
        ReaderRenderBase.__init__(self, extensions)

    @property
    def lexer(self):
        return self.__lexer

    @property
    def node(self):
        return self.__node

    """
    def read(self, input):
        with open(filename, 'r') as fid:
            text = fid.read()
        return self.parse(text)
    """

    def parse(self, node, root=None):
        ast = root if root else tokens.Token(None)

        if isinstance(node, unicode):
            node = page.PageNodeBase(content=node)

        elif isinstance(node, page.PageNodeBase):
            self.__node = node
            #self.__lexer._node = node
        else:
            raise TypeError("The supplied content must be a unicode or PageNodeBase object.")

        self.__lexer.tokenize(node.content, ast)

        return ast

    def add(self, *args):#name, regex, func, location=-1):
        self.__lexer.add(*args)

class MarkdownReader(Reader):
    def __init__(self, ext=None):
        super(MarkdownReader, self).__init__(lexer=RecursiveLexer(moosedown.BLOCK, moosedown.INLINE),
                                             extensions=ext)
