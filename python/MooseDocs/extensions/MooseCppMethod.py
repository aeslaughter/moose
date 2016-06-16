import re
import os
import MooseDocs
from MooseSourcePatternBase import MooseSourcePatternBase
import utils

class MooseCppMethod(MooseSourcePatternBase):
    """
    A markdown extension for including complete source code files.
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[Ch])::(\w+)\s*(.*?)\)'

    def __init__(self):
        super(MooseCppMethod, self).__init__(self.CPP_RE, 'cpp')

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Update the settings from regex match
        self.updateSettings(match.group(5))

        path = os.path.join(MooseDocs.MOOSE_DIR, 'framework')

        #TODO: Make this a configure option or something generic?
        parser = utils.MooseSourceParser(path)


        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        rel_filename = match.group(3).lstrip('/')
        filename = MooseDocs.MOOSE_DIR.rstrip('/') + os.path.sep + rel_filename

        # Print progress
        print utils.colorText('Parsing method "{}" from {}'.format(match.group(4), filename), 'YELLOW')

        # Read the file and create element
        el = self.checkFilename(filename)
        if el == None:
            parser.parse(filename)
            decl, defn = self._parser.method(match.group(4))
            el = self.createElement(match.group(2), defn, filename, rel_filename)

        # Return the Element object
        return el
