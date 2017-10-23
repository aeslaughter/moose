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

    The content must be supplied upon construction and isn't designed to be modified.
    """
    def __init__(self, content=None, **kwargs):
        super(String, self).__init__(**kwargs)
        self.__content = None
        if content is not None:
            self.content = content

    @property
    def content(self):
        """
        Return the content of the String token.
        """
        return self.__content

    @content.setter
    def content(self, value):
        if not isinstance(value, str):
            raise TypeError("The content must be a str, but {} was provided." \
                            .format(type(value)))
        self.__content = value

    def __repr__(self):
        return '{}: {}'.format(self.name, repr(self.content))

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
    def __init__(self, count=1, **kwargs):
        super(Space, self).__init__(**kwargs)
        self.content = ' '
        self.__count = None
        self.count = count # Use setter so type checking is applied

    @property
    def count(self):
        """
        Return the count property.
        """
        return self.__count

    @count.setter
    def count(self, value):
        """
        Set the count property.

        Input:
            value[int]: Desired number of spaces.
        """
        if not isinstance(value, int):
            raise TypeError("The count must be an int, but {} was provided." \
                            .format(type(value)))
        self.__count = value

    def __repr__(self):
        return '{}: count={}'.format(self.name, self.count)

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
    def __init__(self, level=None, **kwargs):
        super(Heading, self).__init__(**kwargs)
        self.__level = None
        self.level = level

    @property
    def level(self):
        """
        Return the heading level property.
        """
        return self.__level

    @level.setter
    def level(self, value):
        """
        Set the heading level property.

        Input:
            value[int]: Desired heading level.
        """
        if not isinstance(value, int):
            raise TypeError("The level must be an int, but {} was provided." \
                            .format(type(value)))
        self.__level = value

    def __repr__(self):
        """
        Includes the level in the tree printing.
        """
        return '{}: level={}'.format(self.name, self.level)

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
    def __init__(self, start=None, **kwargs):
        super(OrderedList, self).__init__(**kwargs)
        self.__start = 1
        if start is not None:
            self.start = start

    @property
    def start(self):
        """
        Return the starting point for the numbered list.
        """
        return self.__start

    @start.setter
    def start(self, value):
        """
        Set the heading level property.

        Input:
            value[int]: Desired heading level.
        """
        if not isinstance(value, int):
            raise TypeError("The start must be an int, but {} was provided." \
                            .format(type(value)))
        self.__start = value

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
    def __init__(self, url=None, **kwargs):
        super(Link, self).__init__(**kwargs)
        self.__url = None
        if url is None:
            raise IOError("The 'url' input is required.")
        self.url = url

    @property
    def url(self):
        """
        Return the url property.
        """
        return self.__url

    @url.setter
    def url(self, value):
        """
        Set the url property.
        """
        if not isinstance(value, str):
            raise TypeError("The url must be an str, but {} was provided." \
                            .format(type(value)))
        self.__url = value

class Shortcut(String):
    def __init__(self, key=None, **kwargs):
        super(Shortcut, self).__init__(**kwargs)
        self.key = key
        self.content = content

    def __repr__(self):
        return '{}: {}={}'.format(self.name, self.key, self.content)

class ShortcutLink(String):
    def __init__(self, key=None, **kwargs):
        super(ShortcutLink, self).__init__(**kwargs)
        self.key = key

    def __repr__(self):
        return '{}: key={}'.format(self.name, self.key)

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
