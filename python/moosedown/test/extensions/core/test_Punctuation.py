#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestPunctuationTokenize(testing.MarkdownTestCase):
    def testBasic(self):
        node = self.ast('a-z')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Punctuation)
        self.assertIsInstance(node(2), tree.tokens.Word)

        self.assertString(node(1).content, '-')

    def testMultiple(self):
        node = self.ast('a-$#%z')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Punctuation)
        self.assertIsInstance(node(2), tree.tokens.Word)
        self.assertString(node(1).content, '-$#%')

    def testCaret(self):
        node = self.ast('a^z')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Punctuation)
        self.assertIsInstance(node(2), tree.tokens.Word)
        self.assertString(node(1).content, '^')

    def testAll(self):
        node = self.ast('Word!@#$%^&*()-=_+{}[]|\":;\'?/>.<,~`   Word')(0)
        self.assertIsInstance(node(0), tree.tokens.Word)
        self.assertIsInstance(node(1), tree.tokens.Punctuation)
        self.assertIsInstance(node(2), tree.tokens.Space)
        self.assertIsInstance(node(3), tree.tokens.Word)
        self.assertString(node(1).content, '!@#$%^&*()-=_+{}[]|\":;\'?/>.<,~`')

if __name__ == '__main__':
    unittest.main(verbosity=2)
