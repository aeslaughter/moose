import re
import markdown
import copy
import logging
import bs4
log = logging.getLogger(__name__)

from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import Pattern
from markdown.extensions.tables import TableProcessor
from markdown.util import etree

import mooseutils
import MooseDocs
from MooseCommonExtension import MooseCommonExtension
from media import MediaExtension, ImagePattern, VideoPattern, SliderBlockProcessor
from include import IncludeExtension, TextPattern, InputPattern, ClangPattern

class FloatExtension(markdown.Extension):
    """
    Extension for adding referenced floats.

    This extension works by modifying existing commands (e.g., !image) and updating the caption.
    """
    def __init__(self, **kwargs):
        super(FloatExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds the figure and table patterns.
        """
        md.registerExtension(self)
        config = self.getConfigs()

        md.requireExtension(MediaExtension)

        ref = FloatReferencePattern(markdown_instance=md, **config)
        md.inlinePatterns.add('moose-reference', ref, '_end')

        link = FloatPostprocessor(markdown_instance=md, **config)
        md.postprocessors.add('moose-reference-link', link, '_end')


def makeExtension(*args, **kwargs):
    return FloatExtension(*args, **kwargs)

class FloatReferencePattern(Pattern):
    """
    Creates a span tag for unknown \ref commands.
    """
    RE = r'(?<![`])(\\ref{(.*?)})'

    def __init__(self, *args, **kwargs):
        Pattern.__init__(self, self.RE, *args)

    def handleMatch(self, match):
        el = etree.Element('span')
        el.text = match.group(2)
        el.set('class', 'moose-unknown-reference')
        el.set('data-moose-float-id',  match.group(3))
        return el

class FloatPostprocessor(Postprocessor):
    """
    """
    def run(self, text):
        soup = bs4.BeautifulSoup(text, 'lxml')

        # Iterator over all calls to \ref
        for ref in soup.find_all('span', class_='moose-unknown-reference'):
            id_ = ref['data-moose-float-id']

            # Search for the desired "id" attribute
            media = soup.find(id=id_)
            if media:

                # Extract ref text items
                cname = media['data-moose-count-name']
                num = media['data-moose-count']

                # Update the reference with a html link
                a = soup.new_tag('a')
                a['class'] = 'moose-reference'
                a['data-moose-reference'] = ref.string
                a['href'] = '#{}'.format(id_)
                a.string = '{} {}'.format(cname.title(), num)
                ref.replace_with(a)

                # Tooltip
                cap = media.find(class_='moose-{}-caption'.format(cname))
                if cap:
                    a['class'] += ' tooltipped'
                    a['data-tooltip'] = unicode(cap.get_text())
                    a['data-position'] = 'top'

            else:
                msg = 'Unknown reference {} in {}'.format(ref.string, self.markdown.current.source())
                log.error(msg)
                ref['class'] += ' tooltipped'
                ref['data-tooltip'] = msg
                ref['data-position'] = 'top'

        return unicode(soup)


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
