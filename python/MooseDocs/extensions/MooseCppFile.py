import re
import os

from markdown.util import etree
import MooseDocs

from MooseCompleteSourcePattern import MooseCompleteSourcePattern

class MooseCppFile(MooseCompleteSourcePattern):
    """
    An extension for displaying complete *.C/*.h file using markdown.

    ![Diffusion](/framework/src/kernels/Diffusion.C)
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[Ch])\s*(.*?)\)'

    def __init__(self):
        super(MooseCompleteSourcePattern, self).__init__(self.CPP_RE)

    def prepareContent(self, content):
        """
        Prepare the convent for conversion to Element object.

        Args:
            content[str]: The content to prepare (i.e., the file contents).
        """

        # Strip header and leading/trailing whitespace and newlines
        if self._settings['strip_header']:
            strt = content.find('/********')
            stop = content.rfind('*******/\n')
            content = content.replace(content[strt:stop+9], '')

        content = MooseCompleteSourcePattern.prepareContent(self, content)

        return content
