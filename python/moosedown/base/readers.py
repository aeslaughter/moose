"""
Defines readers that convert raw text into an AST.
"""
import copy
import anytree
import textwrap
import logging

import moosedown
from moosedown import common
from moosedown.common import exceptions
from moosedown.tree import tokens, page
from lexers import RecursiveLexer
from ConfigObject import ConfigObject, TranslatorObject

LOG = logging.getLogger(__name__)

class Reader(ConfigObject, TranslatorObject):
    """
    Base class for reading (parsing) files into AST.

    Inputs:
       lexer[lexers.Lexer]: Object responsible for applying tokenization (see lexers.py).
       **kwargs: key-value pairs passed to configuration settings (see ConfigObject.py).

    Usage:
    In general, it is not necessary to deal directly with the Reader beyond initial construction.
    The reader should be passed into the Translator, which handles all the necessary calls.
    """
    def __init__(self, lexer, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        TranslatorObject.__init__(self)
        self.__lexer = lexer
        self.__components = []

    def reinit(self):
        """
        Call the Component reinit() methods.
        """
        for comp in self.__components:
            comp.reinit()

    @property
    def lexer(self):
        """
        Retun the Lexer object for the reader, this is useful for preforming nested parsing as
        is the case for the markdown parsing done by MooseDocs, see core.py for examples.
        """
        return self.__lexer

    def parse(self, root, content):
        """
        Perform the parsing of the supplied content into an AST with the provided root node.

        Inputs:
            root[tokens.Token]: The root node for the AST.
            content[unicode:tree.page.PageNodeBase]: The content to parse, either as a unicode
                                                     string or a page node object.
        """

        # Type checking
        if not isinstance(root, tokens.Token):
            msg = "The parse method 'root' argument requires a {} object, but a {} was provided."
            raise MooseDocsException(msg, tokens.Token, type(root))

        node = page.PageNodeBase(content=content) if isinstance(content, unicode) else content
        if not isinstance(node, page.PageNodeBase):
            raise TypeError("The supplied content must be a unicode or PageNodeBase object, but {} was provided.".format(type(node)))

        # Tokenize
        self.reinit()
        self.__lexer.tokenize(root, self.__lexer.grammer(), node.content)

        # Report errors
        for token in anytree.PreOrderIter(root):
            if isinstance(token, tokens.Exception):
                self._exceptionHandler(token)

    def add(self, group, name, component, location='_end'):
        """
        Extened the Reader by adding a TokenComponent.

        Inputs:
            group[str]: Name of the lexer group to append.
            name[str]: The name of the component being added.
            component[components.TokenComponent]: The tokenize component to add.
            location[str|int]: The location to insert this component (see Grammer.py)
        """
        # Check types
        if not isinstance(group, str):
            msg = "The parse method 'group' argument requires a {} object, but a {} was provided."
            raise MooseDocsException(msg, str, type(group))

        if not isinstance(name, str):
            msg = "The parse method 'name' argument requires a {} object, but a {} was provided."
            raise MooseDocsException(msg, str, type(name))

        if not isinstance(component, components.TokenComponent):
            msg = "The parse method 'root' argument requires a {} object, but a {} was provided."
            raise MooseDocsException(msg, tokens.Token, type(component))

        if not isinstance(location, str):
            msg = "The parse method 'location' argument requires a {} object, but a {} was provided."
            raise MooseDocsException(location, str, type(location))

        self.__components.append(component)
        component.init(self.translator)
        self.__lexer.add(group, name, component.RE, component, location)

    @staticmethod
    def _exceptionHandler(token):
        """
        The Lexer converts all TokenizeException caught during tokenization into tokens.Exception
        tokens. This allows the tokenization to report all errors at once and allow for the AST and
        rendering to be performed. This method is simply a convience function for reporting the
        exceptions to the logging system.
        """
        n = 100
        title = []
        if isinstance(token.root.page, page.LocationNodeBase):
            title += textwrap.wrap(u"An exception occurred while tokenizing, the exception was " \
                                   u"raised when executing the {} object while processing the " \
                                   u"following content.".format(token.info.pattern.name), n)
            title += [u"{}:{}".format(token.root.page.source, token.info.line)]
        else:
            title += textwrap.wrap(u"An exception occurred on line {} while tokenizing, the " \
                                   u"exception was raised when executing the {} object while " \
                                   u"processing the following content." \
                                   .format(token.info.line, token.info.pattern.name), n)

        box = moosedown.common.box(token.info[0], line=token.info.line, width=n)
        LOG.exception(u'\n{}\n{}\n{}\n\n'.format(u'\n'.join(title), box, token.traceback))

class MarkdownReader(Reader):
    """
    Reader designed to work with the 'block' and 'inline' structure of markdown to html conversion.
    """
    def __init__(self, **kwargs):
        Reader.__init__(self,
                        lexer=RecursiveLexer(moosedown.BLOCK, moosedown.INLINE),
                        **kwargs)

    def addBlock(self, component, location='_end'):
        """
        Add a component to the 'block' grammer.
        """
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        Reader.add(self, moosedown.BLOCK, name, component, location)

    def addInline(self, component, location='_end'):
        """
        Add an inline component to the 'inline' grammer.
        """
        name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        Reader.add(self, moosedown.INLINE, name, component, location)
