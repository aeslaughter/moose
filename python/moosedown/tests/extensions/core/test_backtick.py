#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestBacktick(testing.MarkdownTestCase):
    """
    Tests inline code.
    """
    def testFenced(self):
        token = self.ast('foo `code` bar')
        self.assertIsInstance(token(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0), tree.tokens.Word)
        self.assertIsInstance(token(0)(1), tree.tokens.Space)
        self.assertIsInstance(token(0)(2), tree.tokens.InlineCode)
        self.assertIsInstance(token(0)(3), tree.tokens.Space)
        self.assertIsInstance(token(0)(4), tree.tokens.Word)

        self.assertString(token(0)(2).code, 'code')

if __name__ == '__main__':
    unittest.main(verbosity=2)
