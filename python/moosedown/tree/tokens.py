"""
This module includes generic tokens that can be used to represent text
in a generic format, i.e., as an abstract syntax tree (AST).
"""
import re
import collections
import logging

import base

LOG = logging.getLogger(__name__)

class Token(base.NodeBase):
    """
    Base class for AST tokens.

    Input:
        *args, **kwarg: (Optional) All arguments and key, value pairs supplied are stored in the
                        settings property and may be retrieved via the various access methods.
    """
    def __init__(self, *args, **kwargs):
        super(Token, self).__init__(*args, **kwargs)
        self.name = self.__class__.__name__
        self.line = None

class String(Token):
    """
    Base class for all tokens meant to contain characters.
    """
    PROPERTIES = [base.Property('content', ptype=str)]

class Unknown(String):
    """
    When the lexer object fails to match a portion of the supplied text then this
    token will be assigned. This should indicate that your grammer definition is incomplete.
    """
    pass

class Word(String):
    """
    Letters without any spaces.
    """
    pass

class Space(String):
    """
    Space token that can define the number of space via count property.
    """
    PROPERTIES = String.PROPERTIES + [base.Property('count', ptype=int, default=1)]
    def __init__(self, *args, **kwargs):
        super(Space, self).__init__(*args, **kwargs)
        self.content = ' '

class Break(Space):
    """
    Line breaks that can define the number of breaks via count property.
    """
    def __init__(self, *args, **kwargs):
        super(Break, self).__init__(*args, **kwargs)
        self.content = '\n'

class Punctuation(String):
    """
    Token for non-letters and non-numbers.
    """
    pass

class Number(String):
    """
    Token for numbers.
    """
    pass

class Code(Token):
    """
    Code content (i.e., Monospace content)
    """
    PROPERTIES = [base.Property('code', ptype=str, required=True),
                  base.Property('language', ptype=str, default='text')]

class Heading(Token):
    """
    Section headings.
    """
    PROPERTIES = [base.Property('level', ptype=int)]

class Paragraph(Token):
    """
    Paragraph token.
    """
    pass

class UnorderedList(Token):
    """
    Token for an un-ordered list (i.e., bulleted list)
    """
    pass

class OrderedList(Token):
    """
    Token for a numbered list.
    """
    PROPERTIES = [base.Property('start', default=1, ptype=int)]

class ListItem(Token):
    """
    List item token.
    """
    def __init__(self, *args, **kwargs):
        Token.__init__(self, *args, **kwargs)
        if not isinstance(self.parent, (OrderedList, UnorderedList)):
            raise IOError("A 'ListItem' must have a 'OrderedList' or 'UnorderedList' parent.")

class Link(Token):
    """
    Token for urls.
    """
    PROPERTIES = [base.Property('url', required=True, ptype=str)]

class Shortcut(Token):
    PROPERTIES = [base.Property('content', required=True, ptype=str),
                  base.Property('key', required=True, ptype=str)]

class ShortcutLink(Token):
    PROPERTIES = [base.Property('key', ptype=str, required=True)]

class InlineCode(Token):
    PROPERTIES = [base.Property('code', ptype=str, required=True)]

class Strong(Token):
    pass

class Emphasis(Token):
    pass

class Underline(Token):
    pass

class Strikethrough(Token):
    pass

class Quote(Token):
    pass

class Superscript(Token):
    pass

class Subscript(Token):
    pass
