#!/usr/bin/env python
"""Testing for MooseDocs.extensions.command MooseDocs extension."""
import unittest

import MooseDocs
from MooseDocs.extensions import command, core, listing, floats
from MooseDocs.tree import tokens, html, latex
from MooseDocs.base import testing, renderers

# TOKEN OBJECTS TESTS
class TestTokens(unittest.TestCase):
    """Test Token object for MooseDocs.extensions.command MooseDocs extension."""

# TOKENIZE TESTS
class TestInlineCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of InlineCommand"""
    EXTENSIONS = [core, command, listing, floats]

    def testToken(self):
        ast = self.ast(u'!listing\nfoo')
        self.assertIsInstance(ast(0), floats.Float)
        self.assertIsInstance(ast(0)(0), tokens.Code)
        self.assertEqual(ast(0)(0).code, u'foo')

    def testTokenWithSettings(self):
        ast = self.ast(u'!listing prefix=bar id=foo-bar\nfoo')
        self.assertIsInstance(ast(0), floats.Float)
        self.assertIsInstance(ast(0)(0), floats.Caption)
        self.assertEqual(ast(0)(0).prefix, u'bar')
        self.assertIsInstance(ast(0)(1), tokens.Code)
        self.assertEqual(ast(0)(1).code, u'foo')

    def testTokenWithSettingsMultiline(self):
        ast = self.ast(u'!listing prefix=bar id=foo-bar\nfoo')
        self.assertIsInstance(ast(0), floats.Float)
        self.assertIsInstance(ast(0)(0), floats.Caption)
        self.assertEqual(ast(0)(0).prefix, u'bar')
        self.assertIsInstance(ast(0)(1), tokens.Code)
        self.assertEqual(ast(0)(1).code, u'foo')


class TestBlockCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of BlockCommand"""

    EXTENSIONS = [core, command, listing, floats]

    def testToken(self):
        ast = self.ast(u'!listing!\nfoo\n!listing-end!')
        self.assertIsInstance(ast(0), floats.Float)
        self.assertIsInstance(ast(0)(0), tokens.Code)
        self.assertEqual(ast(0)(0).code, u'foo\n')

    def testTokenWithSettings(self):
        ast = self.ast(u'!listing! prefix=bar id=foo-bar\nfoo\n!listing-end!')
        self.assertIsInstance(ast(0), floats.Float)
        self.assertIsInstance(ast(0)(0), floats.Caption)
        self.assertEqual(ast(0)(0).prefix, u'bar')
        self.assertIsInstance(ast(0)(1), tokens.Code)
        self.assertEqual(ast(0)(1).code, u'foo\n')

    def testTokenWithSettingsMultiline(self):
        ast = self.ast(u'!listing! prefix=bar\n id=foo-bar\nfoo\n!listing-end!')
        self.assertIsInstance(ast(0), floats.Float)
        self.assertIsInstance(ast(0)(0), floats.Caption)
        self.assertEqual(ast(0)(0).prefix, u'bar')
        self.assertIsInstance(ast(0)(1), tokens.Code)
        self.assertEqual(ast(0)(1).code, u'foo\n')

class TestCommandBaseTokenize(testing.MooseDocsTestCase):
    """Test tokenization of CommandBase"""
    pass # base class

class TestCommandComponentTokenize(testing.MooseDocsTestCase):
    """Test tokenization of CommandComponent"""
    pass # base class

# RENDERER TESTS
if __name__ == '__main__':
    unittest.main(verbosity=2)
