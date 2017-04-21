import re
import markdown
import copy
import logging
log = logging.getLogger(__name__)

from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import Pattern
from markdown.extensions.tables import TableProcessor
from markdown.util import etree

import mooseutils
import MooseDocs
from MooseCommonExtension import MooseCommonExtension
from media import MediaExtension, ImagePattern, VideoPattern, SliderBlockProcessor
from include import IncludeExtension, TextPattern, InputPattern, ClangPattern

class FloatExtension(markdown.Extension):
    """
    Extension for adding referenced floats.

    This extension works by modifying existing commands (e.g., !image) and updating the caption.
    """
    def __init__(self, **kwargs):
        super(FloatExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds the figure and table patterns.
        """
        md.registerExtension(self)
        config = self.getConfigs()

        md.requireExtension(MediaExtension)


def makeExtension(*args, **kwargs):
    return FloatExtension(*args, **kwargs)
