#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestStringTokenize(testing.MooseDocsTestCase):
    """
    Test components that are children of String component
    """
    def testBreak(self):
        token = self.ast('foo\nbar')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)
        self.assertIsInstance(token(1), tree.tokens.Break)
        self.assertIsInstance(token(2), tree.tokens.Word)
        self.assertEqual(token(1).count, 1)

    def testSpace(self):
        token = self.ast('foo bar')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)
        self.assertIsInstance(token(1), tree.tokens.Space)
        self.assertIsInstance(token(2), tree.tokens.Word)
        self.assertEqual(token(1).count, 1)

        token = self.ast('foo     bar')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)
        self.assertIsInstance(token(1), tree.tokens.Space)
        self.assertIsInstance(token(2), tree.tokens.Word)
        self.assertEqual(token(1).count, 5)

    def testPunctuation(self):
        token = self.ast('foo-bar')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)
        self.assertIsInstance(token(1), tree.tokens.Punctuation)
        self.assertIsInstance(token(2), tree.tokens.Word)
        self.assertEqual(token(1).content, '-')

        token = self.ast('foo-:;bar')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)
        self.assertIsInstance(token(1), tree.tokens.Punctuation)
        self.assertIsInstance(token(2), tree.tokens.Word)
        self.assertEqual(token(1).content, '-:;')

    def testNumber(self):
        token = self.ast('foo42bar')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)
        self.assertIsInstance(token(1), tree.tokens.Number)
        self.assertIsInstance(token(2), tree.tokens.Word)
        self.assertEqual(token(1).content, '42')

    def testWord(self):
        token = self.ast('foo')(0)
        self.assertIsInstance(token, tree.tokens.Paragraph)
        self.assertIsInstance(token(0), tree.tokens.Word)

if __name__ == '__main__':
    unittest.main(verbosity=2)
