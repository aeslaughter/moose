#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestUnorderedListTokenize(testing.MooseDocsTestCase):
    """
    Tests inline code.
    """
    def testBasic(self):
        token = self.ast('- foo\n- bar')
        self.assertIsInstance(token(0), tree.tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tree.tokens.Word)

        self.assertIsInstance(token(0)(1), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tree.tokens.Word)

    def testSeparate(self):
        token = self.ast('- foo\n\n\n- bar')
        self.assertIsInstance(token(0), tree.tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tree.tokens.Word)

        self.assertIsInstance(token(1), tree.tokens.UnorderedList)
        self.assertIsInstance(token(1)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(1)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(1)(0)(0)(0), tree.tokens.Word)

    def testNesting(self):
        token = self.ast('- foo\n\n  - nested\n  - list\n- bar')
        self.assertIsInstance(token(0), tree.tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tree.tokens.Word)

        self.assertIsInstance(token(0)(0)(1), tree.tokens.UnorderedList)
        self.assertIsInstance(token(0)(0)(1)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(1)(1), tree.tokens.ListItem)

        self.assertIsInstance(token(0)(1), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tree.tokens.Word)

    def testNestedCode(self):
        token = self.ast('- foo\n  ```language=text\n  code\n  ```\n')
        token = self.ast('- foo\n\n  ```language=text\n  code\n  ```\n')
        self.assertIsInstance(token(0), tree.tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(1), tree.tokens.Code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
