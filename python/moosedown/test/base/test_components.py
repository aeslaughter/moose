#!/usr/bin/env python
"""
Tests for Component objects.
"""
import unittest

from moosedown.base.components import Component

class TestComponent(unittest.TestCase):

    def testBasic(self):
        comp = Component()
        print dir(comp)
        #self.assertEqual(comp.translator, None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
