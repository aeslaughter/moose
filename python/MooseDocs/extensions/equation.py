import os
from markdown.util import etree
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern

import MooseDocs
from MooseCommonExtension import MooseCommonExtension


class EquationExtension(markdown.Extension):
    """
    Adds extension for MathJax equation reference support.
    """
    def extendMarkdown(self, md, md_globals):
        """
        Adds \eqref support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.inlinePatterns.add('moose_equation_reference', EquationPattern(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return EquationExtension(*args, **kwargs)


class EquationPattern(MooseCommonExtension, Pattern):
    """
    Defines syntax for referencing MathJax equations with \label defined.

    This should be handled automatically by MathJax, but I can't seem to get the \eqref stuff working via MathJax. I am
    guessing that the python-markdown-math package is doing something to break compatibility. I also can't get
    latex math to work without the package, so until I have more time to dig I am just building the references manually.
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
