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
        parent[Token|None]: The parent node, if set to None the create Token will be the root node
                            in the resulting tree structure.

        kwargs: (Optional) Any key, value pairs supplied are stored in the settings property
                and may be retrieved via the various access methods.
    """
    def __init__(self, parent=None, **kwargs):
        super(Token, self).__init__(parent, **kwargs)
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

class Unknown(Token):
    """
    When the Grammer object fails to match a portion of the supplied text then this
    token will be assigned. This should indicate that your Grammer definition is incomplete.
    Additionally, this should be used in renderers to produce proper error messages.
    """
    def __init__(self, parent, content=None, **kwargs):
        super(Unknown, self).__init__(parent, **kwargs)
        self.content = content

    def __repr__(self):
        """
        Adds the content to the output for this node.
        """
        return '{}: {}'.format(self.name, self.content)

class String(Token):
    def __init__(self, parent, content=None, **kwargs):
        super(String, self).__init__(parent, **kwargs)
        self.content = content

    def __repr__(self):
        return '{}: {}'.format(self.name, repr(self.content))

class Word(String):
    pass

class Space(String):
    def __init__(self, parent, count=None, **kwargs):
        super(Space, self).__init__(parent, **kwargs)
        self.content = ' '
        self.count = count

    def __repr__(self):
        return '{}: count={}'.format(self.name, self.count)

class Break(Space):
    def __init__(self, parent, count=None, **kwargs):
        super(Break, self).__init__(parent, count=count, **kwargs)
        self.content = '\n'


class Indent(String):
    pass
    #def __init__(self, **kwargs):
    #    super(Indent, self).__init__()

class Punctuation(String):
    pass

class Number(String):
    pass

class Code(Token):
    def __init__(self, parent, code=None, **kwargs):
        super(Code, self).__init__(parent, **kwargs)
        self.code = code

class Heading(Token):
    def __init__(self, parent, level=None, **kwargs):
        super(Heading, self).__init__(parent, **kwargs)
        #TODO: error if level not provided
        self.level = level

    def __repr__(self):
        return '{}: level={}'.format(self.name, self.level)

class Paragraph(Token):
    pass

class UnorderedList(Token):
    pass

class OrderedList(Token):
    def __init__(self, parent, start=None, **kwargs):
        super(OrderedList, self).__init__(parent, **kwargs)
        self.start = start

class ListItem(Token):
    pass

class Link(Token):
    def __init__(self, parent, **kwargs):
        if 'url' not in kwargs:
            pass #TODO: error, or make required settings
        super(Link, self).__init__(parent, **kwargs)
        #self.url = url #TODO: error if url not provided

    def __repr__(self):
        return '{}: url={}'.format(self.name, self['url'])

class Shortcut(Token):
    def __init__(self, parent, key=None, content=None, **kwargs):
        super(Shortcut, self).__init__(parent, **kwargs)
        self.key = key
        self.content = content

    def __repr__(self):
        return '{}: {}={}'.format(self.name, self.key, self.content)

class ShortcutLink(String):
    def __init__(self, parent, key=None, **kwargs):
        super(ShortcutLink, self).__init__(parent, **kwargs)
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
