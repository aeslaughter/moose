#!/usr/bin/env python
import unittest
import mock

import hit

import moosedown
from moosedown.commands.build import DEFAULT_EXTENSIONS, load_extensions, load_object

class TestLoadExtensions(unittest.TestCase):
    def testEmpty(self):
        ext = load_extensions(None, 'foo')
        names = set([e.__module__ for e in ext])
        self.assertEqual(names, set(DEFAULT_EXTENSIONS))

    def testDisableDefaults(self):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))

        ext = load_extensions(ext, '')
        self.assertEqual(ext, [])

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        ext.addChild(hit.NewSection('foo'))

        ext = load_extensions(ext, 'foo')
        self.assertEqual(ext, [])

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter.", args[0])

    @mock.patch('logging.Logger.error')
    def testModuleImportError(self, mock):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        foo = hit.NewSection('foo')
        foo.addChild(hit.NewField('type', hit.FieldKind.String, 'Bad'))
        ext.addChild(foo)

        ext = load_extensions(ext, 'foo')

        self.assertEqual(ext, [])
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("Failed to import the '%s' module.", args[0])

class TestLoadReader(unittest.TestCase):
    def testEmpty(self):
        obj = load_object(None, 'foo', moosedown.base.MarkdownReader)
        self.assertIsInstance(obj, moosedown.base.MarkdownReader)

    @mock.patch('logging.Logger.error')
    def testNode(self, mock):
        node = hit.NewSection('Reader')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'moosedown.base.MarkdownReader'))

        obj = load_object(node, 'foo', moosedown.base.MarkdownReader)

        mock.assert_not_called()
        self.assertIsInstance(obj, moosedown.base.MarkdownReader)

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        node = hit.NewSection('Reader')

        obj = load_object(node, 'foo', moosedown.base.MarkdownReader)
        self.assertIsInstance(obj, moosedown.base.MarkdownReader)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter, using the default", args[0])

class TestLoadRenderer(unittest.TestCase):
    def testEmpty(self):
        obj = load_object(None, 'foo', moosedown.base.MaterializeRenderer)
        self.assertIsInstance(obj, moosedown.base.MaterializeRenderer)

    @mock.patch('logging.Logger.error')
    def testNode(self, mock):
        node = hit.NewSection('Renderer')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'moosedown.base.HTMLRenderer'))

        obj = load_object(node, 'foo', moosedown.base.MaterializeRenderer)
        mock.assert_not_called()
        self.assertIsInstance(obj, moosedown.base.HTMLRenderer)

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        node = hit.NewSection('Renderer')

        obj = load_object(node, 'foo', moosedown.base.MaterializeRenderer)
        self.assertIsInstance(obj, moosedown.base.MaterializeRenderer)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter, using the default", args[0])

    @mock.patch('logging.Logger.error')
    def testBadTypeError(self, mock):
        node = hit.NewSection('Renderer')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'wrong'))

        obj = load_object(node, 'foo', moosedown.base.MaterializeRenderer)
        self.assertIsInstance(obj, moosedown.base.MaterializeRenderer)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The parameter '%s' must contain a valid object name, using the default", args[0])

class TestLoadTranslator(unittest.TestCase):
    def testEmpty(self):
        obj = load_object(None, 'foo', moosedown.base.Translator, moosedown.base.MarkdownReader(), moosedown.base.MaterializeRenderer())
        self.assertIsInstance(obj, moosedown.base.Translator)

    @mock.patch('logging.Logger.error')
    def testNode(self, mock):
        node = hit.NewSection('Translator')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'moosedown.base.Translator'))

        obj = load_object(node, 'foo', moosedown.base.Translator, moosedown.base.MarkdownReader(), moosedown.base.MaterializeRenderer())
        mock.assert_not_called()
        self.assertIsInstance(obj, moosedown.base.Translator)

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        node = hit.NewSection('Translator')

        obj = load_object(node, 'foo', moosedown.base.Translator, moosedown.base.MarkdownReader(), moosedown.base.MaterializeRenderer())
        self.assertIsInstance(obj, moosedown.base.Translator)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter, using the default", args[0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
