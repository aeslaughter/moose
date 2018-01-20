#!/usr/bin/env python
"""
Tests for Component objects.
"""
import unittest
import inspect

from moosedown.common import exceptions
from moosedown.base.components import Component
from moosedown.base import Translator

class TestComponent(unittest.TestCase):
    """
    Test Component base class.
    """
    def testExceptions(self):
        comp = Component()

        with self.assertRaises(exceptions.MooseDocsException) as e:
            comp.translator
        self.assertIn("Component object must be initialized", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            comp.init(42)
        self.assertIn("The supplied object must be of type", e.exception.message)

        #TODO: Get this working...
        #t = Translator()
        #with self.assertRaises(exceptions.MooseDocsException) as e:
        #    comp.init(t)
        #self.assertIn("The component has already been", e.exception.message)

class TestTokenComponent(unittest.TestCase):
    """
    Test TokenComponent.
    """
    def test

if __name__ == '__main__':
    unittest.main(verbosity=2)
