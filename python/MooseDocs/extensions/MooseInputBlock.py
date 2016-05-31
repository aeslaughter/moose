import os
import MooseDocs
from MooseCompleteSourcePattern import MooseCompleteSourcePattern
from FactorySystem import ParseGetPot

class MooseInputBlock(MooseCompleteSourcePattern):
    """
    Markdown extension for extracting blocks from input files.
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[i])::(\w+)\s*(.*?)\)'

    def __init__(self):
        super(MooseInputBlock, self).__init__(self.CPP_RE, 'text')

    def handleMatch(self, match):
        """
        Process the input file supplied.
        """

        # Update the settings from regex match
        self.updateSettings(match.group(5))

        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        rel_filename = match.group(3).lstrip('/')
        filename = MooseDocs.MOOSE_DIR.rstrip('/') + os.path.sep + rel_filename

        # Read the file and create element
        el = self.checkFilename(filename)
        if el == None:
            parser = ParseGetPot(filename)
            node = parser.root_node.getNode(match.group(4))

            if node == None:
                content = 'ERROR: Failed to find {} in {}.'.format(match.group(2), rel_filename)
            else:
                content = node.createString()

            label = '{} [{}]'.format(match.group(2), match.group(4))
            el = self.createElement(label, content, filename, rel_filename)

        return el
