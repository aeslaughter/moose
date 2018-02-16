"""
This module includes generic tokens that can be used to represent text
in a generic format, i.e., as an abstract syntax tree (AST).
"""
import re
import collections
import logging

from MooseDocs.tree.base import Property, NodeBase
#from MooseDocs.base.lexers import LexerInformation

LOG = logging.getLogger(__name__)

class Token(NodeBase):
    """
    Base class for AST tokens.

    Input:
        *args, **kwarg: (Optional) All arguments and key, value pairs supplied are stored in the
                        settings property and may be retrieved via the various access methods.
    """
    PROPERTIES = [Property('recursive', default=True), # This can go away
                  Property('page', required=False), # only exists on root...make a Root node
                  Property('string', ptype=unicode)]
    #base.Property('info')] # change to meta

    def __init__(self, parent=None, name=None, **kwargs):
        self._info = kwargs.pop('info', None)
        #self.__page = kwargs.pop('page', None)
        super(Token, self).__init__(parent, name, **kwargs)
        self.name = self.__class__.__name__
        if self.string is not None: #pylint: disable=no-member
            String(self, content=self.string) #pylint: disable=no-member

    @property
    def info(self):
        node = self
        while node._info is None:
            node = node.parent
        return node._info

    @info.setter
    def info(self, value):
        self._info = value
            #for child in self.children:
            #    child.info = value

#TODO: create class Root that requies page
#TODO: info should be a Property

class CountToken(Token):
    """
    Token that maintains counts based on prefix, the Translator clears the counts prior to building.
    """
    PROPERTIES = Token.PROPERTIES + [Property('prefix', ptype=unicode),
                                     Property('number', ptype=int)]
    COUNTS = collections.defaultdict(int)
    def __init__(self, *args, **kwargs):
        Token.__init__(self, *args, **kwargs)

        if self.prefix is not None:
            CountToken.COUNTS[self.prefix] += 1
            self.number = CountToken.COUNTS[self.prefix]

class Section(Token):
    pass

class String(Token):
    """
    Base class for all tokens meant to contain characters.
    """
    PROPERTIES = Token.PROPERTIES + [Property('content', ptype=unicode)]

class Exception(Token):
    """
    When the lexer object fails create a token, an error token will be created.
    """
    PROPERTIES = Token.PROPERTIES + [Property('traceback', required=False, ptype=str)]

class Word(String):
    """
    Letters without any spaces.
    """
    pass

class Space(String):
    """
    Space token that can define the number of space via count property.
    """
    PROPERTIES = String.PROPERTIES + [Property('count', ptype=int, default=1)]
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
    PROPERTIES = Token.PROPERTIES + [Property('code', ptype=unicode, required=True),
                                     Property('language', ptype=unicode, default=u'text'),
                                     Property('escape', ptype=bool, default=True)]

class Heading(Token):
    """
    Section headings.
    """
    PROPERTIES = [Property('level', ptype=int)]
    def __init__(self, *args, **kwargs):
        Token.__init__(self, *args, **kwargs)

        id_ = self.get('id', None)
        if id_:
            Shortcut(self.root, key=id_, link=u'#{}'.format(id_), token=self)


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
    PROPERTIES = Token.PROPERTIES + [Property('start', default=1, ptype=int)]

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
    PROPERTIES = Token.PROPERTIES + [Property('url', required=True, ptype=unicode),
                                     Property('tooltip', default=True)]

class Shortcut(Token):
    """
    Create a Shortcut that will be used to create a database of keys for use by ShortcutLink tokens.

    When creating Shortcut tokens they should be added to the root level of the tree, for example
    consider the Heading token. Also, refer to core.RenderShortcutLink for how these are used when
    rendering.

    Properties:
        key[unicode]: (Required) The shortcut key, i.e., the string used to look up content in a
                      database, the key is what is used within a ShortcutLink, the content is then
                      pulled from this token. If the 'content' and 'tokens' are empty, then the key
                      is also used for the shortcut text, see RenderShortcutLink.
        link[unicode]: (Required) The content to which the shortcut links against, e.g., the value
                       of 'href' for HTML.
        content[unicode]: (Optional) When present the text provided is used for the link text, this
                          option may not be used with 'tokens'.
        tokens[tuple]: (Optional) When present the tokens provided are rendered and used for the
                       link text, this option may not be used with 'content'.
    """
    PROPERTIES = Token.PROPERTIES + [Property('key', required=True, ptype=unicode),
                                     Property('link', required=True, ptype=unicode),
                                     Property('content', required=False, ptype=unicode),
                                     Property('token', required=False, ptype=Token)]

    def __init__(self, *args, **kwargs):
        Token.__init__(self, *args, **kwargs)

        if self.content and self.token:
            raise ValueError("Both the 'content' and 'token' properties may not be set.")

class ShortcutLink(Token):
    PROPERTIES = Token.PROPERTIES + [Property('key', ptype=unicode, required=True)]

class Monospace(Token):
    PROPERTIES = Token.PROPERTIES + [Property('code', ptype=unicode, required=True)]

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
    PROPERTIES = Token.PROPERTIES + [Property('text', required=True, ptype=unicode)]

class Float(Token):
    PROPERTIES = Token.PROPERTIES + [Property('id', ptype=str),
                                     Property('caption', ptype=unicode),
                                     Property('label', ptype=str, required=True)]
