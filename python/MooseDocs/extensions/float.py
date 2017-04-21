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
