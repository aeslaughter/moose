import re
import markdown
from markdown.treeprocessors import InlineProcessor
import logging
log = logging.getLogger(__name__)

from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import Pattern
from markdown.util import etree

import mooseutils
from MooseCommonExtension import MooseCommonExtension
from media import ImagePattern

class FloatExtension(markdown.Extension):
    """
    Extension for adding referenced floats (e.g., table, figure).
    """
    def extendMarkdown(self, md, md_globals):
        """
        Adds the figure and table patterns.
        """
        md.registerExtension(self)
        config = self.getConfigs()

        # Figures
        fig_count = FloatCountPreprocessor(markdown_instance=md, pattern=FigurePattern.RE, **config)
        md.preprocessors.add('moose_figure_count', fig_count, '_begin')

        fig = FigurePattern(markdown_instance=md, count=fig_count, **config)
        md.inlinePatterns.add('moose_figure', fig, '_begin')

        fig_ref = FloatReferencePattern(markdown_instance=md, count=fig_count, **config)
        md.inlinePatterns.add('moose_figure_reference', fig_ref, '>moose_figure')

        #unknown = UnknownReferencePattern(markdown_instance=md, **config)
        #md.inlinePatterns.add('moose_unknown_reference', unknown, '_end')

def makeExtension(*args, **kwargs):
    return FloatExtension(*args, **kwargs)


class FloatCountPreprocessor(Preprocessor, MooseCommonExtension):
    """
    Tool for counting the number of floats (figures, tables, etc.)
    """

    def __init__(self, markdown_instance=None, pattern=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Preprocessor.__init__(self, markdown_instance)

        self._re = pattern
        self._floats = dict()

    def run(self, lines):

        self._floats = dict()
        index = 0
        for match in re.finditer(self._re, '\n'.join(lines), flags=re.MULTILINE):
            match_id = re.search(r'id\s*=\s*([A-Za-z0-9_\-:]+)', match.group(2))
            if match_id:
                index += 1
                self._floats[match_id.group(1)] = index
        return lines

    def getFloats(self):
        return self._floats


class FigurePattern(ImagePattern):
    """
    Defines syntax for adding images as numbered figures with labels that can be referenced.
    """
    RE = r'^!figure\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, markdown_instance=None, count=None, **kwargs):
        super(FigurePattern, self).__init__(markdown_instance, **kwargs)

        if not isinstance(count, FloatCountPreprocessor):
            raise mooseutils.MooseException("The supplied preprocessor must be a FloatCountPreprocessor, but {} provided.".format(type(count)))

        self._count = count
        self._settings['prefix'] = 'Figure'
        self._settings['id'] = None

    def handleMatch(self, match):
        """
        Creates the html for a numbered MOOSE figure.
        """

        # Locate the float numbers
        floats = self._count.getFloats()

        # Extract information from the regex match
        rel_filename = match.group(2)
        settings = self.getSettings(match.group(3))

        # Error if the 'label' setting is not provided
        if not settings['id']:
            return self.createErrorElement("The 'id' setting must be supplied for the figure: {}".format(rel_filename))

        # Update the caption to include the numbered prefix
        num = floats[settings['id']]
        if settings['caption']:
            settings['caption'] = '{} {}: {}'.format(settings['prefix'], num, settings['caption'])
        else:
            settings['caption'] = '{} {}'.format(settings['prefix'], num)

        # Create the element and store the number
        el = self.createImageElement(rel_filename, settings)
        return el


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
        Dislpay the figure number.
        """
        floats = self._count.getFloats()
        float_id = match.group(2)
        if float_id in floats:
            el = etree.Element('a')
            el.set('class', 'moose-figure-reference')
            el.set('href', '#' + match.group(2))
            el.text = str(floats[match.group(2)])
            return el

class UnknownReferencePattern(Pattern):
    def __init__(self, *args, **kwargs):
        Pattern.__init__(self, FloatReferencePattern.RE, *args, **kwargs)

    def handleMatch(self, match):
        el = etree.Element('span')
        el.text = match.group(1)
        el.set('color', 'rgb(255,1,1)')
        return el
