"""
Syntax for including MOOSE source, input, and markdown files.
"""
import re
import os
import cgi
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
from markdown.util import etree

import MooseDocs
from MooseCommonExtension import MooseCommonExtension

from FactorySystem import ParseGetPot

try:
    import mooseutils.MooseSourceParser
    HAVE_MOOSE_CPP_PARSER = True
except:
    HAVE_MOOSE_CPP_PARSER = False

class IncludeExtension(markdown.Extension):
    """
    Extension for recursive including of partial or complete markdown files.
    """

    def extendMarkdown(self, md, md_globals):
        """
        Adds include support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.preprocessors.add('moose_markdown_include', MarkdownPreprocessor(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return IncludeExtension(*args, **kwargs)

class MarkdownPreprocessor(MooseCommonExtension, Preprocessor):
    """
    An recursive include command for including a markdown file from within another. This adds the ability
    to specify start/end string to include only portions for the markdown.
    """

    RE = r'^!include\s+(.*?)(?:$|\s+)(.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['start'] = (None, "A portion of text that unique identifies the starting location for including text, if not provided the beginning of the file is utilized.")
        settings['end'] = (None, "A portion of text that unique identifies the ending location for including text, if not provided the end of the file is used. By default this line is not included in the display.")
        settings['include_end'] = (False, "When True the texted captured by the 'end' setting is included in the displayed text.")
        return settings

    def __init__(self, *args, **kwargs):
        super(MarkdownPreprocessor, self).__init__(*args, **kwargs)
        self._found = False

    def replace(self, match):
        """
        Substitution function for the re.sub function.
        """
        filename = MooseDocs.abspath(match.group(1))
        settings = self.getSettings(match.group(2))
        if not os.path.exists(filename):
            msg = "Failed to located filename in following command.\n{}"
            el = self.createErrorElement(msg.format(match.group(0)), title="Unknown Markdown File")
            return etree.tostring(el)
        else:
            if settings['start'] or settings['end']:
                content = TextPattern.extractLineRange(filename, settings['start'], settings['end'], settings['include_end'])
            else:
                with open(filename, 'r') as fid:
                    content = fid.read()
            self._found = True
            return content

    def run(self, lines):
        """
        Recursive markdown replacement.
        """
        content = '\n'.join(lines)
        match = True
        while(match):
            self._found = False
            content = re.sub(self.RE, self.replace, content, flags=re.MULTILINE)
            if not self._found:
                break
        return content.splitlines()
