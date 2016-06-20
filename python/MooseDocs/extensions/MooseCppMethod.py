import re
import os
from markdown.util import etree
import logging
log = logging.getLogger(__name__)


import MooseDocs
from MooseSourcePatternBase import MooseSourcePatternBase
import utils

class MooseCppMethod(MooseSourcePatternBase):
    """
    A markdown extension for including complete source code files.
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[Ch])::(\w+)\s*(.*?)\)'

    def __init__(self, src):
        super(MooseCppMethod, self).__init__(self.CPP_RE, src, 'cpp')


    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Update the settings from regex match
        self.updateSettings(match.group(5))

        # Extract relative filename
        rel_filename = match.group(3).lstrip('/')

        # Read the file and create element
        ret = self.checkFilename(rel_filename)
        if ret == None:
            el = self.createErrorElement(rel_filename)
        else:
            key, filename = ret
            make = self._source[key].get('make', None)
            repo = self._source[key].get('repo', None)

            if make == None:
                log.error('The location of the Makefile must be supplied to parser.')
                el = self.createErrorElement(rel_filename)
            else:
                log.info('Parsing method "{}" from {}'.format(match.group(4), filename))

                parser = utils.MooseSourceParser(make)
                parser.parse(filename)
                decl, defn = parser.method(match.group(4))
                el = self.createElement(match.group(2), defn, filename, rel_filename, repo)

        # Return the Element object
        return el
