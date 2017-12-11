import copy
import moosedown
from moosedown.tree import tokens
from lexers import RecursiveLexer

from ReaderRenderBase import ReaderRenderBase

class Reader(ReaderRenderBase):

    def __init__(self, lexer, extensions=None):
        self.__lexer = lexer

        ReaderRenderBase.__init__(self, extensions)

    @property
    def lexer(self):
        return self.__lexer

    def read(self, filename):
        with open(filename, 'r') as fid:
            text = fid.read()
        return self.parse(text)

    def parse(self, text, root=None):
        ast = root if root else tokens.Token(root)
        self.__lexer.tokenize(text, ast)
        return ast

    def add(self, *args):#name, regex, func, location=-1):
        self.__lexer.add(*args)

class MarkdownReader(Reader):
    def __init__(self, ext=None):
        super(MarkdownReader, self).__init__(lexer=RecursiveLexer(moosedown.BLOCK, moosedown.INLINE),
                                             extensions=ext)
