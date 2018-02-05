#!/usr/bin/env python
import unittest

from moosedown import tree
from moosedown.base import testing

class TestSpaceTokenize(testing.MooseDocsTestCase):
    def testBasic(self):
        node = self.ast(u'sit      amet')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Space)
        self.assertIsInstance(node(2), tree.tokens.Word)

        self.assertString(node(0).content, 'sit')
        self.assertString(node(1).content, ' ')
        self.assertEqual(node(1).count, 6)
        self.assertString(node(2).content, 'amet')

if __name__ == '__main__':
    unittest.main(verbosity=2)
