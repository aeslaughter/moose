"""
Defines Reader objects that convert raw text into an AST.
"""
import textwrap
import logging

import anytree

import moosedown
from moosedown import common
from moosedown.tree import tokens, page
from lexers import RecursiveLexer
from __internal__ import ConfigObject, TranslatorObject

LOG = logging.getLogger(__name__)

class Reader(ConfigObject, TranslatorObject):
    """
    Base class for reading (parsing) files into AST.

    Inputs:
       lexer[lexers.Lexer]: Object responsible for applying tokenization (see lexers.py).
       **kwargs: key-value pairs passed to configuration settings (see ConfigObject.py).

    Usage:
        In general, it is not necessary to deal directly with the Reader beyond construction.
        The reader should be passed into the Translator, which handles all the necessary calls.

    TODO: Currently, this requires a RecursiveLexer. It would be nice for the sake of being
          general if this class worked with a Lexer as well.
    """
    def __init__(self, lexer, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        TranslatorObject.__init__(self)
        common.check_type('lexer', lexer, RecursiveLexer)
        self.__lexer = lexer
        self.__components = []

    @property
    def lexer(self):
        """
        Retun the Lexer object for the reader, this is useful for preforming nested parsing as
        is the case for the markdown parsing done by MooseDocs, see core.py for examples.
        """
        return self.__lexer

    def components(self):
        """
        Return the list of components.
        """
        return self.__components

    def reinit(self):
        """
        Call the Component reinit() methods.
        """
        for comp in self.__components:
            comp.reinit()

    def parse(self, root, content):
        """
        Perform the parsing of the supplied content into an AST with the provided root node.

        Inputs:
            root[tokens.Token]: The root node for the AST.
            content[unicode:tree.page.PageNodeBase]: The content to parse, either as a unicode
                                                     string or a page node object.
        """

        # Type checking
        common.check_type('root', root, tokens.Token)
        common.check_type('content', content, (unicode, page.PageNodeBase))
        node = page.PageNodeBase(content=content) if isinstance(content, unicode) else content

        # Tokenize
        self.reinit()
        self.__lexer.tokenize(root, self.__lexer.grammer(), node.content)

        # Report errors
        for token in anytree.PreOrderIter(root):
            if isinstance(token, tokens.Exception):
                self._exceptionHandler(token)

    def add(self, group, component, location='_end'):
        """
        Add a component to Extened the Reader by adding a TokenComponent.

        Inputs:
            group[str]: Name of the lexer group to append.
            component[components.TokenComponent]: The tokenize component to add.
            location[str|int]: The location to insert this component (see Grammer.py)
        """
        common.check_type("group", group, str)
        common.check_type("component", component, moosedown.base.components.TokenComponent)
        common.check_type("location", location, (str, int))

        # Define the name of the component being added (for sorting within Grammer)
        #name = '{}.{}'.format(component.__module__, component.__class__.__name__)
        name = component.__class__.__name__

        # Store and init component, checking self.initialized() allows this object to be used
        # without the Translator which is useful in some cases.
        self.__components.append(component)
        if self.initialized():
            component.init(self.translator)

        # Update the lexer
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
            title += textwrap.wrap(u"An error occurred while tokenizing, the exception was " \
                                   u"raised when executing the {} object while processing the " \
                                   u"following content.".format(token.info.pattern.name), n)
            title += [u"{}:{}".format(token.root.page.source, token.info.line)]
        else:
            title += textwrap.wrap(u"An error occurred on line {} while tokenizing, the " \
                                   u"exception was raised when executing the {} object while " \
                                   u"processing the following content." \
                                   .format(token.info.line, token.info.pattern.name), n)

        box = moosedown.common.box(token.info[0], line=token.info.line, width=n)
        LOG.error(u'\n%s\n%s\n%s\n\n', u'\n'.join(title), box, token.traceback)

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
        Reader.add(self, moosedown.BLOCK, component, location)

    def addInline(self, component, location='_end'):
        """
        Add an inline component to the 'inline' grammer.
        """
        Reader.add(self, moosedown.INLINE, component, location)
