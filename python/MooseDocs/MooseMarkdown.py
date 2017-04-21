import os
import markdown
import logging
log = logging.getLogger(__name__)

import MooseDocs
from MooseDocs.commands.MooseDocsMarkdownNodeBase import MooseDocsMarkdownNodeBase

class MooseMarkdown(markdown.Markdown):
    """
    A custom Markdown object for handling raw text, markdown files, or MooseDocsMarkdownNode objects.

    Additionally, this class automatically loads the required markdown extensions.

    The key to this class is allowing the Markdown object to work with MooseDocsMarkdownNode objects such that the
    extension objects, namely MooseTemplate, could have access to the node object to allow for searching the tree
    for other pages. This should allow for cross page figure, equation, and table links to be created.
    """

    def __init__(self, extensions=[], extension_configs=dict()):

        self.current = None # member for holding the current MooseDocsMarkdownNodeBase object
        super(MooseMarkdown, self).__init__(extensions=extensions, extension_configs=extension_configs)

    def convert(self, node):
        """
        Convert the raw text, markdown file, or node to html.

        Args:
            content[str]: A markdown file or markdown content.
        """
        self.current = None
        if isinstance(node, MooseDocsMarkdownNodeBase):
            with open(node.source(), 'r') as fid:
                md = fid.read().decode('utf-8')
            self.current = node
            log.debug('Parsing markdown: {}'.format(node.source()))
            html = super(MooseMarkdown, self).convert(md)
            self.current = None
            return html
        elif os.path.isfile(node):
            with open(node, 'r') as fid:
                md = fid.read().decode('utf-8')
            return super(MooseMarkdown, self).convert(md)
        else:
            return super(MooseMarkdown, self).convert(node)
