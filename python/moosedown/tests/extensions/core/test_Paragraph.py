#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestParagraph(testing.MarkdownTestCase):
    """
    Test components that are children of String component
    """
    def testParagraph(self):
        for i in range(2, 5):
            token = self.ast('foo{}bar'.format('\n'*i))
            self.assertIsInstance(token(0), tree.tokens.Paragraph)
            self.assertIsInstance(token(0)(0), tree.tokens.Word)

            self.assertIsInstance(token(1), tree.tokens.Paragraph)
            self.assertIsInstance(token(1)(0), tree.tokens.Word)

if __name__ == '__main__':
    unittest.main(verbosity=2)
