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
from MooseCommonExtension import MooseCommonExtension

class TableExtension(markdown.Extension):
    """
    Extension for adding !table command for controlling
    """
    def extendMarkdown(self, md, md_globals):
        """
        Adds Bibtex support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.parser.blockprocessors.add('moose_table', MooseTableProcessor(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return TableExtension(*args, **kwargs)

class MooseTableProcessor(MooseCommonExtension, TableProcessor):
    """
    A special version of the built-in markdown tables that applies a caption and additional css.
    """
    RE = r'^!table\s*(?P<settings>.*?)$'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['caption'] = (None, "The caption text to place after the float heading and number.")
        settings['counter'] = ('table', "The name of the global counter to utilized for numbering.")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
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

        # Get the counter name
        cname = settings['counter']
        if cname is None:
            log.mooseError('The "counter" setting must be a valid string ({})'.format(self.markdown.current.source()))
            cname = 'media'

        # Create the containing <div> tag.
        div = self.applyElementSettings(etree.SubElement(parent, 'div'), settings)
        div.set('class', 'moose-table-div')
        MooseDocs.extensions.increment_counter(div, settings, cname)

        # Create the caption tag
        caption = MooseDocs.extensions.caption_element(settings)
        div.insert(0, caption)

        # Create the table
        TableProcessor.run(self, div, blocks)
