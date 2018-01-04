#!/usr/bin/env python
import unittest
import mock

import moosedown


class TestTranslator(unittest.TestCase):
    """
    Test basic functionality and error handling of Translator object.
    """
    def testConstruction(self):
        """
        Test most basic construction.
        """
        translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                               moosedown.base.HTMLRenderer)

        self.assertIsInstance(translator.reader, moosedown.base.MarkdownReader)
        self.assertIsInstance(translator.renderer, moosedown.base.HTMLRenderer)


    def testConstructionTypeError(self):
        """
        Test type error for reader/renderer arguments.
        """

        # Reader
        with self.assertRaises(TypeError) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader(),
                                                   moosedown.base.HTMLRenderer)
        self.assertIn("The supplied reader must be a 'type'", str(e.exception))

        # Renderer
        with self.assertRaises(TypeError) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                                   moosedown.base.HTMLRenderer())
        self.assertIn("The supplied renderer must be a 'type'", str(e.exception))


    def testReaderRendererInheritError(self):
        """
        Test for the correct base class for the supplied Reader/Renderer types.
        """

        # Reader
        with self.assertRaises(TypeError) as e:
            translator = moosedown.base.Translator(moosedown.base.HTMLRenderer,
                                                   moosedown.base.HTMLRenderer)
        self.assertIn("The supplied reader must inherit from", str(e.exception))

        # Renderer
        with self.assertRaises(TypeError) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                                   moosedown.base.MarkdownReader)
        self.assertIn("The supplied renderer must inherit from", str(e.exception))

    def testExtensionsFromModule(self):
        """
        Test that extensions can be loaded from a module.
        """
        translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                               moosedown.base.HTMLRenderer,
                                               extensions=[moosedown.extensions.core])

        self.assertIn('moosedown.extensions.core.Paragraph',
                      translator.reader.lexer.grammer('block').patterns)

        self.assertIn('moosedown.extensions.core.Space',
                      translator.reader.lexer.grammer('inline').patterns)

    def testExtensionsFromString(self):
        """
        Test that extensions can be loaded from a string.
        """
        translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                               moosedown.base.HTMLRenderer,
                                               extensions=['moosedown.extensions.core'])

        self.assertIn('moosedown.extensions.core.Paragraph',
                      translator.reader.lexer.grammer('block').patterns)

        self.assertIn('moosedown.extensions.core.Space',
                      translator.reader.lexer.grammer('inline').patterns)

    def testExtensionsErrors(self):
        """
        Test that extensions can be loaded from a string.
        """
        with self.assertRaises(ImportError) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                                   moosedown.base.HTMLRenderer,
                                                   extensions=[moosedown.extensions])
            self.assertIn("The supplied module 'moosedown.extensions' must have a 'make_extension'",
                          str(e.exception))


    @mock.patch('moosedown.extensions.core.make_extension',
                return_value=(1, moosedown.extensions.core.CoreRenderExtension()))
    def testMakeExtensionReaderReturnTypeError(self, mock):
        with self.assertRaises(TypeError) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                                   moosedown.base.HTMLRenderer,
                                                   extensions=[moosedown.extensions.core])
        self.assertIn("The first return item (reader object)", str(e.exception))
        self.assertIn("a 'int' object was found", str(e.exception))

    @mock.patch('moosedown.extensions.core.make_extension',
                return_value=(moosedown.extensions.core.CoreMarkdownExtension(), 1))
    def testMakeExtensionRenderReturnTypeError(self, mock):
        with self.assertRaises(TypeError) as e:
            translator = moosedown.base.Translator(moosedown.base.MarkdownReader,
                                                   moosedown.base.HTMLRenderer,
                                                   extensions=[moosedown.extensions.core])
        self.assertIn("The second return item (render object)", str(e.exception))
        self.assertIn("a 'int' object was found", str(e.exception))



if __name__ == '__main__':
    unittest.main(verbosity=2)
