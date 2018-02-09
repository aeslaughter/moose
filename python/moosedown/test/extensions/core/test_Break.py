#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestBreakTokenize(testing.MooseDocsTestCase):
    """Code tokenize"""

    def testBasic(self):
        node = self.ast(u'foo\nbar')(0)
        self.assertIsInstance(node, tree.tokens.Paragraph)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Break)
        self.assertIsInstance(node(2), tree.tokens.Word)
        self.assertEqual(node(1).content, '\n')
        self.assertEqual(node(1).count, 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
t
