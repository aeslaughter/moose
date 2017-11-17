#!/usr/bin/env python
import unittest

from moosedown import tree
from moosedown.base import testing

class TestNumberTokenize(testing.MarkdownTestCase):
    def testBasic(self):
        node = self.ast('sit amet, consectetur')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Space)
        self.assertIsInstance(node(2), tree.tokens.Word)
        self.assertIsInstance(node(3), tree.tokens.Punctuation)
        self.assertIsInstance(node(4), tree.tokens.Space)
        self.assertIsInstance(node(5), tree.tokens.Word)

        self.assertString(node(0).content, 'sit')
        self.assertString(node(2).content, 'amet')
        self.assertString(node(3).content, ',')
        self.assertString(node(5).content, 'consectetur')

if __name__ == '__main__':
    unittest.main(verbosity=2)
