import os
import sys
import re
import unittest
import inspect
import logging

from moosedown import base
from mooseutils import text_diff

logging.basicConfig()



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
        self._translator = base.Translator(self.READER, self.RENDERER, self.EXTENSIONS, **self.CONFIG)

    def ast(self, md):
        """
        Convert supplied markdown text to AST.

        Inputs:
            md[str]: Raw markdown content.
        """
        return self._translator.ast(md)

    def html(self, md):
        #TODO: die
        return self.render(md)

    def render(self, md):
        """
        Convert the supplied markdown to Rendered tree

        Inputs:
            ast: Markdown token tree.
        """
        ast = self.ast(md) if isinstance(md, str) else md
        return self._translator.renderer.render(ast)

    def write(self, md):
        """
        Convert supplied markdown to text
        """
        ast = self.ast(md) if isinstance(md, str) else md
        text = self.render(md)
        return re.sub(r'\n+', '\n', text)

    def assertString(self, content, gold):
        """
        Assert the rendered html string.

        Inputs:
            ast: HTML tree.
        """
        self.assertEqual(content, gold, text_diff(content, gold))
