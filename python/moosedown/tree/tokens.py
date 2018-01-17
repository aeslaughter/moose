"""
This module includes generic tokens that can be used to represent text
in a generic format, i.e., as an abstract syntax tree (AST).
"""
import re
import collections
import logging

import base
from moosedown.base.Grammer import Grammer

LOG = logging.getLogger(__name__)

class Token(base.NodeBase):
    """
    Base class for AST tokens.

    Input:
        *args, **kwarg: (Optional) All arguments and key, value pairs supplied are stored in the
                        settings property and may be retrieved via the various access methods.
    """
    PROPERTIES = [base.Property('line', ptype=int),
                 # base.Property('source', ptype=str), #TODO: get rid of this, it should be handled by exception
                  base.Property('match')]
    def __init__(self, *args, **kwargs):
        super(Token, self).__init__(*args, **kwargs)
        self.name = self.__class__.__name__

class Section(Token):
    pass

class String(Token):
    """
    Base class for all tokens meant to contain characters.
    """
    PROPERTIES = Token.PROPERTIES + [base.Property('content', ptype=unicode)]

class Exception(Token):
    """
    When the lexer object fails create a token, an error token will be created.
    """
    PROPERTIES = Token.PROPERTIES + [base.Property('pattern', required=True, ptype=Grammer.Pattern),
                                     base.Property('traceback', required=True, ptype=str),
                                     base.Property('source', required=True, ptype=str)]

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
        self.content = u' '

class Break(Space):
    """
    Line breaks that can define the number of breaks via count property.
    """
    def __init__(self, *args, **kwargs):
        super(Break, self).__init__(*args, **kwargs)
        self.content = u'\n'

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
    PROPERTIES = [base.Property('code', ptype=unicode, required=True),
                  base.Property('language', ptype=unicode, default=u'text'),
                  base.Property('escape', ptype=bool, default=True)]

class Heading(Token):
    """
    Section headings.
    """
    PROPERTIES = [base.Property('level', ptype=int)]
    def __init__(self, *args, **kwargs):
        Token.__init__(self, *args, **kwargs)

        id_ = self.get('id', None)
        if id_:
            Shortcut(self.root, key=id_, link=u'#{}'.format(id_), tokens=self.children)


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
    PROPERTIES = [base.Property('url', required=True, ptype=unicode)]

class Shortcut(Token):
    """
    Create a Shortcut that will be used to create a database of keys for use by ShortcutLink tokens.

    When creating Shortcut tokens they should be added to the root level of the tree, for example
    consider the Heading token. Also, refer to core.RenderShortcutLink for how these are used when
    rendering.

    Properties:
        key[unicode]: (Required) The shortcut key, i.e., the string used to look up content in a database,
                      the key is what is used within a ShortcutLink, the content is then pulled from this
                      token. If the 'content' and 'tokens' are empty, then the key is also used for the
                      shortcut text, see RenderShortcutLink.
        link[unicode]: (Required) The content to which the shortcut links against, e.g., the value of 'href'
                       for HTML.
        content[unicode]: (Optional) When present the text provided is used for the link text, this option
                          may not be used with 'tokens'.
        tokens[tuple]: (Optional) When present the tokens provided are rendered and used for the link text,
                       this option may not be used with 'content'.
    """
    PROPERTIES = [base.Property('key', required=True, ptype=unicode),
                  base.Property('link', required=True, ptype=unicode),
                  base.Property('content', required=False, ptype=unicode),
                  base.Property('tokens', required=False, ptype=tuple)]

    def __init__(self, *args, **kwargs):
        Token.__init__(self, *args, **kwargs)

        if self.content and self.tokens:
            raise ValueError("Both the 'content' and 'tokens' properties may not be set.")


class ShortcutLink(Token):
    PROPERTIES = [base.Property('key', ptype=unicode, required=True)]

class InlineCode(Token):
    PROPERTIES = [base.Property('code', ptype=unicode, required=True)]

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

class Label(Token):
    PROPERTIES = [base.Property('text', required=True, ptype=unicode)]

class Float(Token):
    PROPERTIES = [base.Property('id', ptype=str), base.Property('caption', ptype=unicode),
                  base.Property('label', ptype=str, required=True)]
