#pylint: disable=missing-docstring
#################################################################
#                   DO NOT MODIFY THIS HEADER                   #
#  MOOSE - Multiphysics Object Oriented Simulation Environment  #
#                                                               #
#            (c) 2010 Battelle Energy Alliance, LLC             #
#                      ALL RIGHTS RESERVED                      #
#                                                               #
#           Prepared by Battelle Energy Alliance, LLC           #
#             Under Contract No. DE-AC07-05ID14517              #
#              With the U. S. Department of Energy              #
#                                                               #
#              See COPYRIGHT for full restrictions              #
#################################################################
import re
import os

import markdown
from markdown.preprocessors import Preprocessor
from markdown.util import etree

import MooseDocs
from MooseCommonExtension import MooseCommonExtension
from listings import ListingPattern

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
        md.preprocessors.add('moose-markdown-include',
                             MarkdownPreprocessor(markdown_instance=md, **config), '>fenced_code_block')

def makeExtension(*args, **kwargs): #pylint: disable=invalid-name
    return IncludeExtension(*args, **kwargs)

class MarkdownPreprocessor(MooseCommonExtension, Preprocessor):
    """
    An recursive include command for including a markdown file from within another. This adds the
    ability to specify start/end string to include only portions for the markdown.
    """
    REGEX = r'^!include\s+(.*?)(?:$|\s+)(.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        l_settings = ListingPattern.defaultSettings()
        settings['re'] = (None, "Python regular expression to use for removing text, with flags set to MULTILINE|DOTALL.")
        settings['start'] = l_settings['start']
        settings['end'] = l_settings['end']
        settings['include-end'] = l_settings['include-end']
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



        if settings['start'] or settings['end']:
            content = ListingPattern.extractLineRange(filename, settings['start'],
                                                          settings['end'], settings['include-end'])
        else:
            with open(filename, 'r') as fid:
                content = fid.read()

        if settings['re']:
            match = re.search(settings['re'], content, flags=re.MULTILINE|re.DOTALL)
            if not match:
                msg = "Failed to located regex in following command.\n{}"
                el = self.createErrorElement(msg.format(settings['re']), title="Failed Regex")
                return etree.tostring(el)
            content = match.group(0)

        self._found = True
        return content

    def run(self, lines):
        """
        Recursive markdown replacement.
        """
        content = '\n'.join(lines)
        match = True
        while match:
            self._found = False
            content = re.sub(self.REGEX, self.replace, content, flags=re.MULTILINE)
            if not self._found:
                break
        return content.splitlines()
