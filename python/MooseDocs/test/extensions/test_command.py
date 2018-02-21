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
        print ast
        self.assertFalse(True)

class TestCommandBaseTokenize(testing.MooseDocsTestCase):
    """Test tokenization of CommandBase"""
    pass # base class

class TestBlockCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of BlockCommand"""

    EXTENSIONS = [core, command, listing, floats]

    def testToken(self):
        self.assertFalse(True)

class TestCommandComponentTokenize(testing.MooseDocsTestCase):
    """Test tokenization of CommandComponent"""
    pass # base class

# RENDERER TESTS
if __name__ == '__main__':
    unittest.main(verbosity=2)
