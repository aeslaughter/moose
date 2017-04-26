import os
import re
import bs4
import collections
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.util import etree
from markdown.inlinepatterns import Pattern
from markdown.treeprocessors import Treeprocessor

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

        link = FloatLinker(markdown_instance=md, **config)
        md.treeprocessors.add('moose-ref-linker', link, '_end')


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
        el = etree.Element('a')
        el.text = match.group(2)
        el.set('class', 'moose-unknown-reference')
        el.set('data-moose-float-id', match.group(3))
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


class FloatLinker(Treeprocessor):

    def __init__(self, markdown_instance=None, **kwargs):
        super(FloatLinker, self).__init__(markdown_instance)

    def run(self, root):

        #soup = bs4.BeautifulSoup(text, "lxml")

        lookup = dict()
        counts = collections.defaultdict(int)

        # Number the floats
        for div in root.iter('div'):
            name = div.get('data-moose-float-name', None)
            if name:
                counts[name] += 1
                lookup[div.get('id').lower()] = (name, counts[name])
                for span in div.iter('span'):
                    if span.get('class') == 'moose-float-caption-heading-number':
                      span.text = str(counts[name])

        # Update references
        for a in root.iter('a'):
            if a.get('class') == 'moose-unknown-reference':
                id_ = a.get('data-moose-float-id').lower()
                if id_ in lookup:
                    name, num = lookup[id_]
                    a.text = '{} {}'.format(name, num)
                    a.set('href', '#{}'.format(name))
                    a.set('class', 'moose-float-reference')



        #print lookup
        #print counts
        #soup.html.unwrap()
        #soup.body.unwrap()
        #return unicode(soup)
