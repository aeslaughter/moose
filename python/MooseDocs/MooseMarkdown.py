#pylint: disable=missing-docstring
####################################################################################################
#                                    DO NOT MODIFY THIS HEADER                                     #
#                   MOOSE - Multiphysics Object Oriented Simulation Environment                    #
#                                                                                                  #
#                              (c) 2010 Battelle Energy Alliance, LLC                              #
#                                       ALL RIGHTS RESERVED                                        #
#                                                                                                  #
#                            Prepared by Battelle Energy Alliance, LLC                             #
#                               Under Contract No. DE-AC07-05ID14517                               #
#                               With the U. S. Department of Energy                                #
#                                                                                                  #
#                               See COPYRIGHT for full restrictions                                #
####################################################################################################
#pylint: enable=missing-docstring
import logging
import collections
import markdown
import mooseutils
from MooseDocs.commands.MarkdownNode import MarkdownNode

LOG = logging.getLogger(__name__)

class MooseMarkdown(markdown.Markdown):
    """
    A custom Markdown object for handling raw text, markdown files, or MarkdownNode objects.

    The key to this class is allowing the Markdown object to work with MarkdownNode objects such
    that the extension objects, namely MooseTemplate, could have access to the node object to allow
    for searching the tree for other pages. This should allow for cross page figure, equation, and
    table links to be created.

    Args:
        config[dict]: The configure dict, if not provided getDefaultExtensions is used.
        config_file[str]: The name of the configuration file to import, this is applied to the
                          supplied or default 'config'.
    """
    CODE_BLOCK_COUNT = 0 # counter for code block copy buttons

    @staticmethod
    def getDefaultExtensions():
        """
        Return an OrderedDict that defines the default configuration for extensions.

        It returns an OrderedDict such that the dict() can serve to populate the list of extensions
        (i.e., the keys) in the desired instantiate order as well as the configuration settings.

        If no settings are needed for the entry simply set the entry to contain an empty dict()

        """
        ext = collections.OrderedDict() # used to maintain insert order

        # http://pythonhosted.org/Markdown/extensions/index.html
        ext['toc'] = dict()
        ext['smarty'] = dict()
        ext['admonition'] = dict()
        ext['extra'] = dict()
        ext['meta'] = dict()

        # pip install python-markdown-math
        ext['mdx_math'] = dict(enable_dollar_delimiter=True)

        # MooseDocs
        ext['MooseDocs.extensions.global'] = dict()
        ext['MooseDocs.extensions.include'] = dict()
        ext['MooseDocs.extensions.bibtex'] = dict()
        ext['MooseDocs.extensions.css'] = dict()
        ext['MooseDocs.extensions.diagram'] = dict()
        ext['MooseDocs.extensions.devel'] = dict()
        ext['MooseDocs.extensions.misc'] = dict()
        ext['MooseDocs.extensions.media'] = dict()
        ext['MooseDocs.extensions.tables'] = dict()
        ext['MooseDocs.extensions.listings'] = dict()
        ext['MooseDocs.extensions.refs'] = dict()
        ext['MooseDocs.extensions.app_syntax'] = dict()
        ext['MooseDocs.extensions.template'] = dict()
        return ext

    def __init__(self, config=None, default=True):

        # Create the default configuration
        ext_config = self.getDefaultExtensions() if default else collections.OrderedDict()

        # Apply the supplied configuration
        if config is not None:
            ext_config.update(config)

        # Define storage for the current MarkdownNode
        self.current = None
        super(MooseMarkdown, self).__init__(extensions=ext_config.keys(),
                                            extension_configs=ext_config)

    def requireExtension(self, required):
        """
        Raise an exception of the supplied extension type is not registered.
        """
        if not self.getExtension(required):
            raise mooseutils.MooseException("The {} extension is required." \
                                            .format(required.__name__))

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
            self.current = MarkdownNode(md, name='')

        return super(MooseMarkdown, self).convert(self.current.content)
