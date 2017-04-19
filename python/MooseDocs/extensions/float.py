import re
import markdown
import copy
import logging
log = logging.getLogger(__name__)

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

        # Figures
        media_ext = md.getExtension(MediaExtension)
        if not media_ext:
            log.warning("Numbered Figures require the MediaExtension.")
        else:
            patterns = [ImagePattern.RE, VideoPattern.RE]
            fig_count = FloatCountPreprocessor(markdown_instance=md, patterns=patterns, **config)
            md.preprocessors.add('moose_figure_count', fig_count, '_begin')

            # Common options for Figure inline patterns
            kwargs = {'HEADING':'Figure', 'markdown_instance':md, 'count':fig_count}
            kwargs.update(config)

            # !image
            fig_image = gen_float(ImagePattern, DIV_CLASS='moose-image-div', **kwargs)
            md.inlinePatterns.add('moose_image_figure', fig_image, '<moose_image')

            # !video
            fig_video = gen_float(VideoPattern, DIV_CLASS='moose-video-div', **kwargs)
            md.inlinePatterns.add('moose_video_figure', fig_video, '<moose_video')

            # !slider
            # Not yet supported...

            fig_ref = FloatReferencePattern(markdown_instance=md, count=fig_count, **config)
            md.inlinePatterns.add('moose_figure_reference', fig_ref, '>moose_video_figure')

        # Tables
        tbl_count = FloatCountPreprocessor(markdown_instance=md, patterns=[MooseTableProcessor.RE], **config)
        md.preprocessors.add('moose_table_count', tbl_count, '_begin')

        tbl = MooseTableProcessor(markdown_instance=md, count=tbl_count, **config)
        md.parser.blockprocessors.add('moose_table', tbl, '_begin')

        tbl_ref = FloatReferencePattern(markdown_instance=md, count=tbl_count, **config)
        md.inlinePatterns.add('moose_table_reference', tbl_ref, '>moose_video_figure')

        # Listings
        include_ext = md.getExtension(IncludeExtension)
        if not include_ext:
            log.warning("Numbered Listings require the IncludeExtension.")
        else:
            include_config = copy.copy(config)
            include_config.update(include_ext.getConfigs())
            patterns = [TextPattern.RE, InputPattern.RE, ClangPattern.RE]

            lst_count = FloatCountPreprocessor(markdown_instance=md, patterns=patterns, **include_config)
            md.preprocessors.add('moose_listing_count', lst_count, '_begin')

            kwargs = {'markdown_instance':md, 'count':lst_count, 'HEADING':'Listing'}
            kwargs.update(include_config)

            listing_text = gen_float(TextPattern, **kwargs)
            md.inlinePatterns.add('moose_text_listing', listing_text, '<moose_text')

            listing_input = gen_float(InputPattern, **kwargs)
            md.inlinePatterns.add('moose_input_listing', listing_input, '<moose_input')

            listing_clang = gen_float(ClangPattern, **kwargs)
            md.inlinePatterns.add('moose_clang_listing', listing_clang, '<moose_clang')

            listing_ref = FloatReferencePattern(markdown_instance=md, count=lst_count, **config)
            md.inlinePatterns.add('moose_listing_reference', listing_ref, '>moose_video_figure')

        unknown = UnknownReferencePattern(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_unknown_reference', unknown, '_end')



def makeExtension(*args, **kwargs):
    return FloatExtension(*args, **kwargs)


class FloatCountPreprocessor(Preprocessor, MooseCommonExtension):
    """
    Tool for counting the number of floats (figures, tables, etc.)
    """

    def __init__(self, markdown_instance=None, patterns=[], **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Preprocessor.__init__(self, markdown_instance)

        self._patterns = patterns
        self._floats = dict()

    def run(self, lines):

        self._floats = dict()
        index = 0
        for pattern in self._patterns:
            for match in re.finditer(pattern, '\n'.join(lines), flags=re.MULTILINE):
                match_id = re.search(r'id\s*=\s*([A-Za-z0-9_\-:]+)', match.group('settings'))
                if match_id:
                    index += 1
                    self._floats[match_id.group(1)] = index
        return lines

    def getFloats(self):
        return self._floats

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

class FloatReferencePattern(MooseCommonExtension, Pattern):
    """
    Defines syntax for referencing figures.
    """
    RE = r'(?<![`])\\ref{(.*?)}'

    def __init__(self, markdown_instance=None, count=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

        if not isinstance(count, FloatCountPreprocessor):
            raise mooseutils.MooseException("The supplied preprocessor must be a FloatCountPreprocessor, but {} provided.".format(type(count)))

        self._count = count

    def handleMatch(self, match):
        """
        Display the figure number.
        """
        floats = self._count.getFloats()
        float_id = match.group(2)
        if float_id in floats:
            el = etree.Element('a')
            el.set('class', 'moose-float-reference')
            el.set('href', '#' + match.group(2))
            el.text = str(floats[match.group(2)])
            return el

class UnknownReferencePattern(Pattern):
    """
    Creates a span tag for unknown \ref commands.
    """
    RE = r'(?<![`])(\\ref{.*?})'

    def __init__(self, *args, **kwargs):
        Pattern.__init__(self, self.RE, *args)

    def handleMatch(self, match):
        el = etree.Element('span')
        el.text = match.group(2)
        el.set('class', 'moose-unknown-reference')
        return el

def gen_float(TEMPLATE, DIV_CLASS='moosedocs-code-div', CAPTION_CLASS='moose-caption',
              HEADING='Listing', **kwargs):
    """
    Generates class for adding listing numbers to existing commands from the include extension.

    Args:
        TEMPLATE: The class type to generate.
    """
    class TextListingPattern(TEMPLATE):
        """
        Adds number listing prefix to code blocks.
        """
        @staticmethod
        def defaultSettings():
            settings = TEMPLATE.defaultSettings()
            return settings

        def __init__(self, markdown_instance=None, count=None, **kwargs):
            super(TextListingPattern, self).__init__(markdown_instance=markdown_instance, **kwargs)
            self._count = count
            self._div_class = DIV_CLASS # location of the "id" tag attribute
            self._caption_class = CAPTION_CLASS
            self._heading = HEADING

        def div(self, el):
            """
            Locates the desired 'div' element.
            """
            div = None
            for item in el.iter('div'):
                is_code = ('class' in item.attrib) and \
                          (self._div_class in item.attrib['class']) and \
                          ('id' in item.attrib) and \
                          item.attrib['id']
                if  is_code:
                    div = item
                    break
            return div

        def caption(self, el):
            """
            Locates the caption <p> tag and returns the element.
            """
            # Locate caption
            cap = None
            for item in el.iter('p'):
                is_cap = ('class' in item.attrib) and \
                         (self._caption_class in item.attrib['class'])
                if is_cap:
                    cap = item

            # Locate parent
            parent = None
            for item in el.iter():
                if cap in list(item):
                    parent = item

            # Remove old caption
            idx = list(parent).index(cap)
            parent.remove(cap)

            return parent, idx, cap

            return cap

        def handleMatch(self, match):
            el = super(TextListingPattern, self).handleMatch(match)
            div = self.div(el)

            if div:
                settings = self.getSettings(match.group('settings'))
                id_ = div.attrib['id']
                floats = self._count.getFloats()
                num = floats[id_]

                # Add new caption
                parent, idx, caption = self.caption(div)
                text = list(caption)[-1].text
                heading = '{} {}: '.format(self._heading, num)
                new_caption = MooseDocs.extensions.caption_element(text=text, heading=heading,     class_='moose-{}-caption'.format(self._heading.lower()))
                parent.insert(idx, new_caption)

            return el

    return TextListingPattern(**kwargs)
