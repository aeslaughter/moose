#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import MooseMarkdown
from moosedown import tree
from moosedown.base import testing

class TestCode(testing.MarkdownTestCase):
    """
    Test fenced code blocks
    """
    def testBasic(self):
        code = self.ast('```\nint x;\n```')(0)
        self.assertIsInstance(code, tree.tokens.Code)
        self.assertEqual(code.code, '\nint x;\n')
        self.assertEqual(code.language, 'text')

    def testLanguage(self):
        code = self.ast('```language=C++\nint x;\n```')(0)
        self.assertIsInstance(code, tree.tokens.Code)
        self.assertEqual(code.code, '\nint x;\n')
        self.assertEqual(code.language, 'text')


if __name__ == '__main__':
    unittest.main(verbosity=2)
