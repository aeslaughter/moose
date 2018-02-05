#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestCodeTokenize(testing.MooseDocsTestCase):
    """Code tokenize"""

    def testBasic(self):
        code = self.ast(u'```\nint x;\n```')(0)
        self.assertIsInstance(code, tree.tokens.Code)
        self.assertString(code.code, '\nint x;\n')
        self.assertString(code.language, 'text')

    def testLanguage(self):
        code = self.ast(u'```language=cpp\nint x;\n```')(0)
        self.assertIsInstance(code, tree.tokens.Code)
        self.assertString(code.code, '\nint x;\n')
        self.assertString(code.language, 'cpp')

if __name__ == '__main__':
    unittest.main(verbosity=2)
