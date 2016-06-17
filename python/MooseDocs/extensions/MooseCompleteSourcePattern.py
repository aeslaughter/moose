import re
import os
import MooseDocs
from MooseSourcePatternBase import MooseSourcePatternBase

class MooseCompleteSourcePattern(MooseSourcePatternBase):
    """
    A markdown extension for including complete source code files.
    """

    def __init__(self, regex, src, language=None):
        super(MooseCompleteSourcePattern, self).__init__(regex, src, language)

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Update the settings from regex match
        self.updateSettings(match.group(4))

        # Read the file
        rel_filename = match.group(3).lstrip('/')
        ret = self.checkFilename(rel_filename)
        if ret == None:
            el = self.creteErrorElement(rel_filename)
        else:
            key, filename = ret
            repo = self._source[key].get('repo', None)

            fid = open(filename)
            content = fid.read()
            fid.close()
            el = self.createElement(match.group(2), content, filename, rel_filename, repo)

        # Return the Element object
        return el
