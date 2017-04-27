import os
import markdown
import collections
import logging
log = logging.getLogger(__name__)

import mooseutils
import MooseDocs
from MooseDocs.commands.MarkdownNode import MarkdownNode
from MooseDocs.extensions.media import MediaPatternBase

class MooseMarkdown(markdown.Markdown):
    """
    A custom Markdown object for handling raw text, markdown files, or MarkdownNode objects.

    Additionally, this class automatically loads the required markdown extensions.

    The key to this class is allowing the Markdown object to work with MarkdownNode objects such that the
    extension objects, namely MooseTemplate, could have access to the node object to allow for searching the tree
    for other pages. This should allow for cross page figure, equation, and table links to be created.
    """
    CODE_BLOCK_COUNT = 0

    def __init__(self, extensions=[], extension_configs=dict()):
        self.current = None # member for holding the current MarkdownNode object
        super(MooseMarkdown, self).__init__(extensions=extensions, extension_configs=extension_configs)

    def requireExtension(self, required):
        """
        Raise an exception of the supplied extension type is not registered.
        """
        if not self.getExtension(required):
            raise mooseutils.MooseException("The {} extension is required.".format(required.__name__))

    def getExtension(self, etype):
        """
        Return an extension instance.

        Args:
            etype[type]: The type of the extension to return.
        """
        out = None
        for ext in self.registeredExtensions:
            if isinstance(ext, etype):
                out = ext
                break
        return out

    def convert(self, md):
        """
        Convert the raw text, markdown file, or node to html.

        Args:
            md[str]: A markdown file, markdown content, or MarkdownNode
        """
        MooseMarkdown.CODE_BLOCK_COUNT = 0
        self.current = None

        if isinstance(md, MarkdownNode):
            self.current = md
        else:
            self.current = MarkdownNode(md)

        return super(MooseMarkdown, self).convert(self.current.content)
