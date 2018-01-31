"""
Module for common unittest related tasks.
"""
import unittest

from moosedown import base
from mooseutils import text_diff

class MarkdownTestCase(unittest.TestCase):
    """
    TestCase object for converting markdown to AST, HTML, and LaTeX.
    """
    EXTENSIONS = ['moosedown.extensions.core']
    READER = base.MarkdownReader
    RENDERER = base.HTMLRenderer
    CONFIG = dict()

    def setUp(self):
        """
        Create the Translator instance.
        """
        self._translator = base.Translator(self.READER, self.RENDERER, self.EXTENSIONS,
                                           **self.CONFIG)

    @property
    def reader(self):
        """Return Reader instance."""
        return self._translator.reader

    @property
    def renderer(self):
        """Return Reader instance."""
        return self._translator.renderer

    def assertString(self, content, gold):
        """
        Assert the rendered html string.

        Inputs:
            ast: HTML tree.
        """
        self.assertEqual(content, gold, text_diff(content, gold))
