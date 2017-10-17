import re
#from MooseDocs.tree import tokens
from MooseDocs import common
from MooseDocs import  lexers

from Reader import Reader

class MarkdownReader(Reader):
    def __init__(self, ext=None):
        super(MarkdownReader, self).__init__(lexer=lexers.MarkdownLexer(), extensions=ext)
