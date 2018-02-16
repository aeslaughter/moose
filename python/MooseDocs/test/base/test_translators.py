#!/usr/bin/env python
"""
Testing for Translator object.
"""
import unittest

from MooseDocs.base import Translator, MarkdownReader, HTMLRenderer
from moosedown.extensions import core
from MooseDocs.common import exceptions

class TestTranslator(unittest.TestCase):
    """
    Test basic functionality and error handling of Translator object.
    """
    def testConstruction(self):
        """
        Test most basic construction.
        """
        translator = Translator(MarkdownReader(), HTMLRenderer())
        self.assertIsInstance(translator.reader, MarkdownReader)
        self.assertIsInstance(translator.renderer, HTMLRenderer)

    def testConstructionTypeError(self):
        """
        Test type error for reader/renderer arguments.
        """

        # Reader
        with self.assertRaises(exceptions.MooseDocsException) as e:
            translator = Translator('foo', HTMLRenderer())
        self.assertIn("The argument 'reader' must be", e.exception.message)

        # Renderer
        with self.assertRaises(exceptions.MooseDocsException) as e:
            translator = Translator(MarkdownReader(), 'foo')
        self.assertIn("The argument 'renderer' must be", e.exception.message)

    def testExtensionsFromModule(self):
        """
        Test that extensions can be loaded from a module.
        """
        t = Translator(MarkdownReader(), HTMLRenderer(), extensions=[core.CoreExtension()])

        self.assertIn('Paragraph',
                      t.reader.lexer.grammer('block'))

        self.assertIn('Space',
                      t.reader.lexer.grammer('inline'))

    def testExtensionsErrors(self):
        """
        Test type error on Extension.
        """
        with self.assertRaises(exceptions.MooseDocsException) as e:
            translator = Translator(MarkdownReader(), HTMLRenderer(), extensions=['foo'])
        self.assertIn("The argument 'extensions' must be", e.exception.message)

if __name__ == '__main__':
    unittest.main(verbosity=2)
