#!/usr/bin/env python
import unittest

from moosedown import tree
from moosedown.base import testing

class TestQuoteTokenize(testing.MooseDocsTestCase):
    def testBasic(self):
        node = self.ast(u'> foo bar')(0)
        self.assertIsInstance(node, tree.tokens.Quote)
        self.assertIsInstance(node(0), tree.tokens.Paragraph)
        self.assertIsInstance(node(0)(0), tree.tokens.Word)
        self.assertIsInstance(node(0)(1), tree.tokens.Space)
        self.assertIsInstance(node(0)(2), tree.tokens.Word)

        self.assertString(node(0)(0).content, 'foo')
        self.assertString(node(0)(1).content, ' ')
        self.assertString(node(0)(2).content, 'bar')

if __name__ == '__main__':
    unittest.main(verbosity=2)
