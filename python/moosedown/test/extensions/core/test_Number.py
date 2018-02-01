#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestNumberTokenize(testing.MooseDocsTestCase):
    def testBasic(self):
        node = self.ast('foo1bar')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Number)
        self.assertIsInstance(node(2), tree.tokens.Word)

if __name__ == '__main__':
    unittest.main(verbosity=2)
