#!/usr/bin/env python
"""
Tests for __internal__.py module.
"""
import unittest
import mock
from moosedown.base.__internal__ import ConfigObject, TranslatorObject

class Foo(ConfigObject):
    """Testing instance of ConfigObject."""
    @staticmethod
    def defaultConfig():
        config = ConfigObject.defaultConfig()
        config['foo'] = ('bar', "Testing...")
        return config

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



if __name__ == '__main__':
    unittest.main(verbosity=2)
