#!/usr/bin/env python
"""
Testing for Translator object.
"""
import unittest
import mock

import moosedown
from moosedown.common import exceptions


class TestTranslator(unittest.TestCase):
    """
    Test basic functionality and error handling of Translator object.
    """
    def testConstruction(self):
        """
        Test most basic construction.
        """
        translator = moosedown.base.Translator(moosedown.base.MarkdownReader(),
                                               moosedown.base.HTMLRenderer())

        self.assertIsInstance(translator.reader, moosedown.base.MarkdownReader)
        self.assertIsInstance(translator.renderer, moosedown.base.HTMLRenderer)


    def testConstructionTypeError(self):
        """
        Test type error for reader/renderer arguments.
        """

        # Reader
        with self.assertRaises(exceptions.MooseDocsException) as e:
            translator = moosedown.base.Translator('foo', moosedown.base.HTMLRenderer())
        self.assertIn("The argument 'reader' must be", e.exception.message)

        # Renderer
        with self.assertRaises(exceptions.MooseDocsException) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader(), 'foo')
        self.assertIn("The argument 'renderer' must be", e.exception.message)

    def testExtensionsFromModule(self):
        """
        Test that extensions can be loaded from a module.
        """
        t = moosedown.base.Translator(moosedown.base.MarkdownReader(),
                                      moosedown.base.HTMLRenderer(),
                                      extensions=[moosedown.extensions.core.CoreExtension()])

        self.assertIn('moosedown.extensions.core.Paragraph',
                      t.reader.lexer.grammer('block'))

        self.assertIn('moosedown.extensions.core.Space',
                      t.reader.lexer.grammer('inline'))

    def testExtensionsErrors(self):
        """
        Test type error on Extension.
        """
        with self.assertRaises(exceptions.MooseDocsException) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader(),
                                                   moosedown.base.HTMLRenderer(),
                                                   extensions=['foo'])
        self.assertIn("The argument 'extensions' must be", e.exception.message)

if __name__ == '__main__':
    unittest.main(verbosity=2)
