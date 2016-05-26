import re
import os
import MooseDocs
from MooseSourcePatternBase import MooseSourcePatternBase

class MooseCompleteSourcePattern(MooseSourcePatternBase):
    """
    A markdown extension for including complete source code files.
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[Chi])\s*(.*?)\)'

    def __init__(self):
        super(MooseCompleteSourcePattern, self).__init__(self.CPP_RE)

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Update the settings from regex match
        self.updateSettings(match.group(4))

        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        rel_filename = match.group(3).lstrip('/')
        filename = MooseDocs.MOOSE_DIR.rstrip('/') + os.path.sep + rel_filename

        # If the file does not exist return a bold block
        if not os.path.exists(filename):
            el = etree.Element('p')
            el.set('style', "color:red;font-size:150%")
            el.text = 'ERROR: Invalid filename: ' + filename
            return el

        # Read the file
        fid = open(filename)
        content = fid.read()
        fid.close()

        return self.createElement(match.group(2), content, rel_filename)
