#!/usr/bin/env python
"""
Tests for __internal__.py module.
"""
import unittest
from moosedown.common import exceptions
from moosedown.base import Translator, MarkdownReader, HTMLRenderer
from moosedown.base.__internal__ import ConfigObject, TranslatorObject

class Foo(ConfigObject):
    """Testing instance of ConfigObject."""
    @staticmethod
    def defaultConfig():
        config = ConfigObject.defaultConfig()
        config['foo'] = ('bar', "Testing...")
        return config

class Bar(ConfigObject):
    """Testing instance of ConfigObject."""
    @staticmethod
    def defaultConfig():
        return None

class TestConfigObject(unittest.TestCase):
    """
    Test basic use of ConfigObject.
    """
    def testConstruction(self):
        """
        Test most basic construction.
        """
        obj = ConfigObject()
        self.assertEqual(obj.getConfig(), dict())

    def testDefaultConfig(self):
        """
        Test defaultConfig returns class level options.
        """
        obj = Foo()
        self.assertEqual(obj.getConfig(), dict(foo='bar'))

    def testBadDefaultConfigReturn(self):
        """
        Test exception from defaultConfig.
        """
        with self.assertRaises(exceptions.MooseDocsException) as e:
            obj = Bar()
        self.assertIn("The return type from 'defaultConfig'", e.exception.message)

    def testUpdateAndGet(self):
        """
        Test update method.
        """
        obj = Foo()
        obj.update(foo='foo')
        self.assertEqual(obj.getConfig(), dict(foo='foo'))
        self.assertEqual(obj['foo'], 'foo')
        self.assertEqual(obj.get('foo'), 'foo')
        self.assertIsNone(obj.get('bar', None))

    def testUnknown(self):
        """
        Test unknown config exception.
        """
        with self.assertRaises(exceptions.MooseDocsException) as e:
            obj = Foo(unknown=42)
        self.assertIn("The following config options", e.exception.message)
        self.assertIn("unknown", e.exception.message)

class TestTranslatorObject(unittest.TestCase):
    """
    Test basic use of TranslatorObject.
    """
    def testBasic(self):
        """
        Test correct use.
        """
        t = Translator(MarkdownReader(), HTMLRenderer())
        obj = TranslatorObject()
        self.assertFalse(obj.initialized())
        obj.init(t)
        self.assertTrue(obj.initialized())
        self.assertIs(obj.translator, t)

    def testExceptions(self):
        """
        Test Exceptions.
        """
        t = Translator(MarkdownReader(), HTMLRenderer())
        obj = TranslatorObject()
        with self.assertRaises(exceptions.MooseDocsException) as e:
            obj.init('')
        self.assertIn("The argument 'translator'", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            obj.translator
        self.assertIn("The init() method of", e.exception.message)

        obj.init(t)
        with self.assertRaises(exceptions.MooseDocsException) as e:
            obj.init(t)
        self.assertIn("already been initialized", e.exception.message)

if __name__ == '__main__':
    unittest.main(verbosity=2)
