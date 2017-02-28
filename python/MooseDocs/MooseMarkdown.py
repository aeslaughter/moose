import os
import markdown
import MooseDocs
import logging
log = logging.getLogger(__name__)


class MooseMarkdown(markdown.Markdown):
    """
    Custom Markdown parser for handling MOOSE flavored markdown.
    """

    def __init__(self, extensions=[], extension_configs=dict(), **kwargs):

        # Add the required packages
        extensions += ['toc', 'smarty', 'admonition', 'extra', 'meta', 'mdx_math', 'markdown_include.include']

        # Configure packages
        for config in ['mdx_math', 'markdown_include.include']:
            if config not in extension_configs:
                extension_configs[config] = dict()
                extension_configs['mdx_math'].setdefault('enable_dollar_delimiter', True)
        extension_configs['markdown_include.include'].setdefault('base_path', MooseDocs.ROOT_DIR)

        super(MooseMarkdown, self).__init__(extensions=extensions, extension_configs=extension_configs, **kwargs)


        self.current = None

    def convert(self, node):
        """
        Convert the markdown for the supplied node and return html and meta data.

        Args:
            content[str]: A markdown file or markdown content.
        """
        with open(node.source(), 'r') as fid:
            md = fid.read().decode('utf-8')

        self.current = node
        log.debug('Parsing markdown: {}'.format(node.source()))
        html = super(MooseMarkdown, self).convert(md)
        self.current = None
        return html, self.Meta
