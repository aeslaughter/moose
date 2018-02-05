"""
Module for common unittest related tasks.
"""
import unittest
import inspect
import logging

from moosedown import base, common, tree
from mooseutils import text_diff

logging.basicConfig()

class MooseDocsTestCase(unittest.TestCase):
    """
    TestCase object for converting markdown to AST, HTML, and LaTeX.
    """
    EXTENSIONS = ['moosedown.extensions.core']
    EXTENSIONS_CONFIG = dict()
    READER = base.MarkdownReader
    RENDERER = base.HTMLRenderer
    CONFIG = dict()

    def setUp(self):
        """
        Create the Translator instance.
        """
        self._reader = self.READER()
        self._renderer = self.RENDERER()
        extensions = common.load_extensions(self.EXTENSIONS, self.EXTENSIONS_CONFIG)
        self._translator = base.Translator(self._reader, self._renderer, extensions,
                                           **self.CONFIG)

    def assertString(self, content, gold):
        """
        Assert the rendered html string.

        Inputs:
            ast: HTML tree.
        """
        self.assertEqual(content, gold, text_diff(content, gold))

    def ast(self, content):
        """
        Create AST from Reader object.
        """
        ast = tree.tokens.Token(None)
        self._reader.parse(ast, content)
        return ast

    def render(self, content):
        """
        Convert text into rendered content.
        """
        _, root = self._translator.convert(content)
        return root#ast, root

def get_parent_objects(module, cls):
    """
    Tool for locating all objects that derive from a certain base class.
    """
    func = lambda obj: inspect.isclass(obj) and issubclass(obj, cls)
    return inspect.getmembers(module, predicate=func)
