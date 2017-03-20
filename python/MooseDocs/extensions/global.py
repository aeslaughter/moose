"""
Extension for adding globals to MooseDocs markdown.
"""
import markdown
from markdown.preprocessors import Preprocessor
import logging
log = logging.getLogger(__name__)

from MooseCommonExtension import MooseCommonExtension

class GlobalExtension(markdown.Extension):
    """
    Extension for adding global markdown style link ids.
    """

    def __init__(self, **kwargs):
        self.config = dict()
        self.config['globals'] = ['', "List of global markdown links (e.g., [foo]: bar)."]
        super(GlobalExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds Bibtex support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.preprocessors.add('moose_globals', GlobalPreprocessor(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return GlobalExtension(*args, **kwargs)

class GlobalPreprocessor(MooseCommonExtension, Preprocessor):
    """
    Appends global links to markdown content
    """
    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs),
        Preprocessor.__init__(self, markdown_instance)
        self._globals = kwargs.pop('globals', [None])

    def run(self, lines):
        """
        Append globals
        """
        return lines + ['[{}]: {}'.format(key, value) for key, value in self._globals.iteritems()]
