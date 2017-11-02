#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestOrderedList(testing.MarkdownTestCase):
    """
    Tests inline code.
    """
    def testBasic(self):
        token = self.ast('1. foo\n1. bar')
        self.assertIsInstance(token(0), tree.tokens.OrderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tree.tokens.Word)
        self.assertIsInstance(token(0)(0)(0)(1), tree.tokens.Break)

        self.assertIsInstance(token(0)(1), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tree.tokens.Word)

    def testStart(self):
        token = self.ast('42. foo\n1. bar')
        self.assertIsInstance(token(0), tree.tokens.OrderedList)
        self.assertEqual(token(0).start, 42)

    def testSeparate(self):
        token = self.ast('1. foo\n\n\n1. bar')
        self.assertIsInstance(token(0), tree.tokens.OrderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tree.tokens.Word)

        self.assertIsInstance(token(1), tree.tokens.OrderedList)
        self.assertIsInstance(token(1)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(1)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(1)(0)(0)(0), tree.tokens.Word)

    def testNesting(self):
        token = self.ast('1. foo\n\n   - nested\n   - list\n1. bar')
        self.assertIsInstance(token(0), tree.tokens.OrderedList)
        self.assertIsInstance(token(0)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tree.tokens.Word)

        self.assertIsInstance(token(0)(0)(1), tree.tokens.UnorderedList)
        self.assertIsInstance(token(0)(0)(1)(0), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(0)(1)(1), tree.tokens.ListItem)

        self.assertIsInstance(token(0)(1), tree.tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tree.tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tree.tokens.Word)

if __name__ == '__main__':
    unittest.main(verbosity=2)
