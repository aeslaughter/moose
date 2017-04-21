"""
Extension for adding globals to MooseDocs markdown.
"""
import markdown
from markdown.preprocessors import Preprocessor
import logging
log = logging.getLogger(__name__)

from markdown.extensions.tables import TableProcessor

from MooseCommonExtension import MooseCommonExtension

class TableExtension(markdown.Extension):
    """
    Extension for adding !table command for controlling
    """

    def __init__(self, **kwargs):
        self.config = dict()
        self.config['globals'] = ['', "List of global markdown links (e.g., [foo]: bar)."]
        super(GlobalExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds Bibtex support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.parser.blockprocessors.add('moose_table', TableProcessor(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return GlobalExtension(*args, **kwargs)

class MooseTableProcessor(MooseCommonExtension, TableProcessor):
    """
    A special version of the built-in markdown tables that applies a caption and additional css.
    """

    RE = r'^!table\s*(?P<settings>.*?)$'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['caption'] = (None, "The caption text to place after the float heading and number.")
        return settings

    def __init__(self, markdown_instance=None, count=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        TableProcessor.__init__(self, markdown_instance.parser)

        if not isinstance(count, FloatCountPreprocessor):
            raise mooseutils.MooseException("The supplied preprocessor must be a FloatCountPreprocessor, but {} provided.".format(type(count)))
        self._count = count
        self._heading = 'Table'

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
        settings = self.getSettings(match.group(1))

        # Create the containing <div> tag.
        div = self.applyElementSettings(etree.SubElement(parent, 'div'), settings)
        div.set('class', 'moose-table')

        # Extract known table floats so the table number can be added to the caption
        floats = self._count.getFloats()
        num = floats[settings['id']]

        # Error if the 'label' setting is not provided
        if not settings['id']:
            return self.createErrorElement("The 'id' setting must be supplied for the table command.")

        # Create the caption tag
        heading = '{} {}: '.format(self._heading, num)
        text = settings['caption']
        caption = MooseDocs.extensions.caption_element(text=text, heading=heading,
                                                       class_='moose-table-caption')
        div.insert(0, caption)

        # Create the table
        TableProcessor.run(self, div, blocks)
