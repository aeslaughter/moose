"""
Extension for adding globals to MooseDocs markdown.
"""
import re
import markdown
from markdown.util import etree
from markdown.preprocessors import Preprocessor
import logging
log = logging.getLogger(__name__)

from markdown.extensions.tables import TableProcessor

import MooseDocs
from MooseMarkdownExtension import MooseMarkdownExtension
from MooseMarkdownCommon import MooseMarkdownCommon

class TableExtension(MooseMarkdownExtension):
    """
    Extension for adding !table command for controlling
    """
    @staticmethod
    def defaultConfig():
        config = MooseMarkdownExtension.defaultConfig()
        return config

    def extendMarkdown(self, md, md_globals):
        """
        Adds Bibtex support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.parser.blockprocessors.add('moose_table', MooseTableProcessor(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs): #pylint: disable=invalid-name
    return TableExtension(*args, **kwargs)

class MooseTableProcessor(MooseMarkdownCommon, TableProcessor):
    """
    A special version of the built-in markdown tables that applies a caption and additional css.
    """
    RE = r'^!table\s*(?P<settings>.*?)$'

    @staticmethod
    def defaultSettings():
        settings = MooseMarkdownCommon.defaultSettings()
        settings['caption'] = (None, "The caption text to place after the float heading and number.")
        settings['counter'] = ('table', "The name of the global counter to utilized for numbering.")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseMarkdownCommon.__init__(self, **kwargs)
        TableProcessor.__init__(self, markdown_instance.parser)

    def test(self, parent, block):
        """
        Test that the block has !table syntax, if it does remove the top line and run the base class
        test method to prepare for creating the actual table.
        """
        match = re.search(self.RE, block, flags=re.MULTILINE)
        if match:
            block = '\n'.join(block.split('\n')[1:])
            return TableProcessor.test(self, parent, block)
        return False

    def run(self, parent, blocks):
        """
        Create a table with caption.
        """

        # Strip the !table line and settings
        lines = blocks[0].split('\n')
        blocks[0] = '\n'.join(lines[1:])
        match = re.search(self.RE, lines[0], flags=re.MULTILINE)
        settings = self.getSettings(match.group('settings'))

        # Create the containing <div> tag.
        div = self.createFloatElement(settings)
        parent.append(div)

        # Create the table
        TableProcessor.run(self, div, blocks)
