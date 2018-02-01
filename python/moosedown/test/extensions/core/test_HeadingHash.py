#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestHeadingHashTokenize(testing.MooseDocsTestCase):
    """
    Tests that hash style headings (#) are converted.
    """
    def testBasic(self):
        ast = self.ast('# Heading with Spaces')
        h = ast(0)
        self.assertIsInstance(h, tree.tokens.Heading)
        self.assertEqual(h.level, 1)
        self.assertIsInstance(h(0), tree.tokens.Label)
        self.assertIsInstance(h(1), tree.tokens.Word)
        self.assertIsInstance(h(2), tree.tokens.Space)
        self.assertIsInstance(h(3), tree.tokens.Word)
        self.assertIsInstance(h(4), tree.tokens.Space)
        self.assertIsInstance(h(5), tree.tokens.Word)
        self.assertEqual(h(1).content, 'Heading')
        self.assertEqual(h(3).content, 'with')
        self.assertEqual(h(5).content, 'Spaces')

    def testLevels(self):
        for i in range(1,7):
            ast = self.ast('{} Heading'.format('#'*i))
            self.assertEqual(ast(0).level, i)

if __name__ == '__main__':
    unittest.main(verbosity=2)
