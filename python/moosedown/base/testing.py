"""
Module for common unittest related tasks.
"""
import unittest
import inspect

from moosedown import base
from mooseutils import text_diff

class MooseDocsTestCase(unittest.TestCase):
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
        self._reader = self.READER()
        self._renderer = self.RENDERER()
        self._translator = base.Translator(self._reader, self._renderer, self.EXTENSIONS,
                                           **self.CONFIG)

    def assertString(self, content, gold):
        """
        Assert the rendered html string.

        Inputs:
            ast: HTML tree.
        """
        self.assertEqual(content, gold, text_diff(content, gold))

def get_parent_objects(module, cls):
    """
    Tool for locating all objects that derive from a certain base class.
    """
    func = lambda obj: inspect.isclass(obj) and issubclass(obj, cls)
    return inspect.getmembers(module, predicate=func)
