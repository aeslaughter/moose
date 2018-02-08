#!/usr/bin/env python
import collections

import unittest
import mock

import hit
import mooseutils
from mooseutils.hit_load import _hit_parse, HitNode

import moosedown
from moosedown.common import exceptions
from moosedown.common.load_config import _hit_load_extensions, _hit_load_object, DEFAULT_EXTENSIONS

def parse_hit(hit_node):
    root = HitNode()
    _hit_parse(root, hit_node, '')
    return root

class TestLoadExtensions(unittest.TestCase):
    def testEmpty(self):
        ext = _hit_load_extensions(None, 'foo')
        names = set([e.__module__ for e in ext])
        self.assertEqual(names, set(DEFAULT_EXTENSIONS))

    def testDisableDefaults(self):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))

        ext = _hit_load_extensions(parse_hit(ext), '')
        self.assertEqual(ext, [])

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        ext.addChild(hit.NewSection('foo'))

        ext = _hit_load_extensions(parse_hit(ext), 'foo')
        self.assertEqual(ext, [])

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter.", args[0])

    def testModuleImportError(self):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        foo = hit.NewSection('foo')
        foo.addChild(hit.NewField('type', hit.FieldKind.String, 'Bad'))
        ext.addChild(foo)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            ext = _hit_load_extensions(parse_hit(ext), 'foo')

        self.assertIn("Failed to import the supplied 'Bad' module.", e.exception.message)

class TestLoadReader(unittest.TestCase):
    def testEmpty(self):
        obj = _hit_load_object(None, 'foo', moosedown.base.MarkdownReader)
        self.assertIsInstance(obj, moosedown.base.MarkdownReader)

    @mock.patch('logging.Logger.error')
    def testNode(self, mock):
        node = hit.NewSection('Reader')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'moosedown.base.MarkdownReader'))

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.MarkdownReader)

        mock.assert_not_called()
        self.assertIsInstance(obj, moosedown.base.MarkdownReader)

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        node = hit.NewSection('Reader')

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.MarkdownReader)
        self.assertIsInstance(obj, moosedown.base.MarkdownReader)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter, using the default", args[0])

class TestLoadRenderer(unittest.TestCase):
    def testEmpty(self):
        obj = _hit_load_object(None, 'foo', moosedown.base.MaterializeRenderer)
        self.assertIsInstance(obj, moosedown.base.MaterializeRenderer)

    @mock.patch('logging.Logger.error')
    def testNode(self, mock):
        node = hit.NewSection('Renderer')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'moosedown.base.HTMLRenderer'))

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.MaterializeRenderer)
        mock.assert_not_called()
        self.assertIsInstance(obj, moosedown.base.HTMLRenderer)

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        node = hit.NewSection('Renderer')

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.MaterializeRenderer)
        self.assertIsInstance(obj, moosedown.base.MaterializeRenderer)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter, using the default", args[0])

    @mock.patch('logging.Logger.error')
    def testBadTypeError(self, mock):
        node = hit.NewSection('Renderer')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'wrong'))

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.MaterializeRenderer)
        self.assertIsInstance(obj, moosedown.base.MaterializeRenderer)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The parameter '%s' must contain a valid object name, using the default", args[0])

class TestLoadTranslator(unittest.TestCase):
    def testEmpty(self):
        obj = _hit_load_object(None, 'foo', moosedown.base.Translator, moosedown.base.MarkdownReader(), moosedown.base.MaterializeRenderer())
        self.assertIsInstance(obj, moosedown.base.Translator)

    @mock.patch('logging.Logger.error')
    def testNode(self, mock):
        node = hit.NewSection('Translator')
        node.addChild(hit.NewField('type', hit.FieldKind.String, 'moosedown.base.Translator'))

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.Translator, moosedown.base.MarkdownReader(), moosedown.base.MaterializeRenderer())
        mock.assert_not_called()
        self.assertIsInstance(obj, moosedown.base.Translator)

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        node = hit.NewSection('Translator')

        obj = _hit_load_object(parse_hit(node), 'foo', moosedown.base.Translator, moosedown.base.MarkdownReader(), moosedown.base.MaterializeRenderer())
        self.assertIsInstance(obj, moosedown.base.Translator)

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter, using the default", args[0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
