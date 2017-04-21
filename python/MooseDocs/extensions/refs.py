import os
import bs4
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.util import etree
from markdown.inlinepatterns import Pattern
from markdown.postprocessors import Postprocessor

import MooseDocs
from MooseCommonExtension import MooseCommonExtension


class RefExtension(markdown.Extension):
    """
    Adds \ref and \eqref support.

    \eqref: works with MathJax equation reference support.
    \ref: works with captions create with MooseDocs (see tables.py, media.py).
    """
    def extendMarkdown(self, md, md_globals):
        """
        Adds \eqref support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()

        md.inlinePatterns.add('moose-eq-ref', EquationPattern(markdown_instance=md, **config), '_begin')

        ref = FloatReferencePattern(markdown_instance=md, **config)
        md.inlinePatterns.add('moose-ref', ref, '_end')

        link = FloatPostprocessor(markdown_instance=md, **config)
        md.postprocessors.add('moose-ref-link', link, '_end')


def makeExtension(*args, **kwargs):
    return RefExtension(*args, **kwargs)

class FloatReferencePattern(Pattern):
    """
    Creates a <span> tag for unknown \ref commands.
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

class EquationPattern(MooseCommonExtension, Pattern):
    """
    Defines syntax for referencing MathJax equations with \label defined.

    This should be handled automatically by MathJax, but I can't seem to get the \eqref stuff
    working via MathJax. I am guessing that the python-markdown-math package is doing something to
    break compatibility. I also can't get latex math to work without the package, so until I have
    more time to dig I am just building the references manually.
    """

    RE = r'(?<!`)\\eqref{(.*?)}'

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

    def handleMatch(self, match):
        """
        Creates the <a> object with the reference that is then updated with the function in the init.js file.
        """
        mjx_id = 'mjx-eqn-{}'.format(match.group(2).replace(':', ''))
        el = etree.Element('a')
        el.set('class', 'moose-equation-reference')
        el.set('href', '#' + mjx_id)
        el.text = '(??)'
        return el

class FloatPostprocessor(Postprocessor):
    """
    Converts the <span> elements created by FloatReferencePattern into proper links to the figure.
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
                a['class'] = 'moose-ref'
                a['data-moose-ref'] = ref.string
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
