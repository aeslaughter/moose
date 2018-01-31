#!/usr/bin/env python
"""
Test for the Reader objects.
"""
import unittest
import re
import logging
logging.basicConfig(level=logging.CRITICAL)

from moosedown.common import exceptions
from moosedown.tree import tokens
from moosedown.base import Reader, RecursiveLexer, TokenComponent

class BlockComponent(TokenComponent):
    """Class for testing MarkdownReader"""
    RE = re.compile('(?P<inline>.*)')
    def __call__(self, info, parent):
        return tokens.Token(parent)

class WordComponent(TokenComponent):
    """Class for testing lexer."""
    RE = re.compile('(?P<content>\w+) *')
    def __call__(self, info, parent):
        content = info['content']
        if content == 'throw':
            raise exceptions.TokenizeException("testing")
        return tokens.Word(parent, content=content)

class TestReader(unittest.TestCase):
    """
    Test basic functionality and error handling of Reader objects.
    """
    def testConstruction(self):
        """
        Test most basic construction.
        """
        lexer = RecursiveLexer('foo')
        reader = Reader(lexer)
        self.assertIs(reader.lexer, lexer)

    def testParse(self):
        """
        Test parsing.
        """
        root = tokens.Token(None)
        reader = Reader(RecursiveLexer('foo'))
        reader.add('foo', WordComponent())
        reader.parse(root, u'foo bar')
        self.assertIsInstance(root(0), tokens.Word)
        self.assertEqual(root(0).content, u'foo')
        self.assertIsInstance(root(1), tokens.Word)
        self.assertEqual(root(1).content, u'bar')

    def testParseExceptions(self):
        """
        Test exceptions on paser method.
        """
        reader = Reader(RecursiveLexer('foo'))
        with self.assertRaises(exceptions.MooseDocsException) as e:
            reader.parse([], u'')
        self.assertIn("The argument 'root'", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            reader.parse(tokens.Token(), [])
        self.assertIn("The argument 'content'", e.exception.message)

    def testAddExceptions(self):
        """
        Test the add method.
        """
        reader = Reader(RecursiveLexer('foo'))
        with self.assertRaises(exceptions.MooseDocsException) as e:
            reader.add([], u'', '')
        self.assertIn("The argument 'group'", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            reader.add('foo', u'', '')
        self.assertIn("The argument 'component'", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            reader.add('foo', TokenComponent(), [])
        self.assertIn("The argument 'location'", e.exception.message)

    def testTokenizeException(self):
        """
        Test parsing with an exception.
        """
        root = tokens.Token(None)
        reader = Reader(RecursiveLexer('foo'))
        reader.add('foo', WordComponent())
        reader.parse(root, u'throw bar')
        self.assertIsInstance(root(0), tokens.Exception)
        self.assertIsInstance(root(1), tokens.Word)
        self.assertEqual(root(1).content, u'bar')

class TestMarkdownReader(unittest.TestCase):
    """
    Test basic function of MarkdownReader.
    """
    def testBasic(self):
        """
        Test the addBlock and addInline methods.
        """
        root = tokens.Token(None)
        reader = Reader(RecursiveLexer('block', 'inline'))
        reader.add('block', BlockComponent())
        reader.add('inline', WordComponent())
        reader.parse(root, u'foo bar')

        self.assertIsInstance(root(0), tokens.Token)
        self.assertIsInstance(root(0)(0), tokens.Word)
        self.assertEqual(root(0)(0).content, u'foo')
        self.assertIsInstance(root(0)(1), tokens.Word)
        self.assertEqual(root(0)(1).content, u'bar')


if __name__ == '__main__':
    unittest.main(verbosity=2)
