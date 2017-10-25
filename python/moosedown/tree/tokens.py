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
        self.__line = None # this gets set by Lexer object for error reporting

    @property
    def line(self):
        """
        Return the line number property.
        """
        return self.__line

    @line.setter
    def line(self, value):
        """
        Set the line property with type checking.

        This setter is called by the Lexer when parsing string so that useful error messages
        can be reported.
        """
        if isinstance(value, int):
            self.__line = value
        else:
            LOG.error('The supplied line number must be of type "int", but "%s" provided.',
                      type(value).__name__)

class String(Token):
    """
    Base class for all tokens meant to contain characters.
    """
    PROPERTIES = [base.Property('content', ptype=str)]

class Unknown(String):
    """
    When the Grammer object fails to match a portion of the supplied text then this
    token will be assigned. This should indicate that your Grammer definition is incomplete.
    Additionally, this should be used in renderers to produce proper error messages.
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
    def __init__(self, **kwargs):
        super(Space, self).__init__(**kwargs)
        self.content = ' '

class Break(Space):
    """
    Line breaks that can define the number of breaks via count property.
    """
    def __init__(self, count=1, **kwargs):
        super(Break, self).__init__(count=count, **kwargs)
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

class Code(String):
    """
    Code content (i.e., Monospace content)
    """
    pass

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

class Shortcut(String):
    PROPERTIES = String.PROPERTIES + [base.Property('key', ptype=str)]

class ShortcutLink(String):
    PROPERTIES = String.PROPERTIES + [base.Property('key', ptype=str)]

class InlineCode(String):
    pass

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
