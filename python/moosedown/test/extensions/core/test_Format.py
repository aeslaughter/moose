#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestFormatTokenize(testing.MooseDocsTestCase):
    """
    Test inline formatting (e.g., *bold*, _italic_, etc.)
    """
    def testStrong(self):
        ast = self.ast(u'+strong+')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")

        ast = self.ast(u'+strong with space\nand a new line+')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testUnderline(self):
        ast = self.ast(u'=underline=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "underline")

        ast = self.ast(u'=underline with space\nand a new line=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "underline")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testEmphasis(self):
        ast = self.ast(u'*emphasis*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")

        ast = self.ast(u'*emphasis with space\nand a new line*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testStrikethrough(self):
        ast = self.ast(u'~strikethrough~')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strikethrough)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strikethrough")

        ast = self.ast(u'~strikethrough with space\nand a new line~')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strikethrough)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strikethrough")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testSubscript(self):
        ast = self.ast(u'S_x_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(0).content, "x")

    def testSuperscript(self):
        ast = self.ast(u'S^x^')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(0).content, "x")

    def testMonospace(self):
        ast = self.ast(u'`x`')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Monospace)
        self.assertEqual(ast(0)(0).code, "x")

        ast = self.ast(u'`*x*`')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Monospace)
        self.assertEqual(ast(0)(0).code, u"*x*")

    def testSuperscriptAndSubscript(self):
        ast = self.ast(u's_y^x^_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

        ast = self.ast(u's^y_x_^')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

    def testNesting(self):
        ast = self.ast(u'=*emphasis* underline=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(0)(0).content, "emphasis")
        self.assertIsInstance(ast(0)(0)(2), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "underline")

        ast = self.ast(u'*=underline= emphasis*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Underline)
        self.assertEqual(ast(0)(0)(0)(0).content, "underline")
        self.assertIsInstance(ast(0)(0)(2), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "emphasis")

        ast = self.ast(u'*=+~strike~ bold+ under= emphasis*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0)(0)(0), tree.tokens.Strikethrough)

        ast = self.ast(u's_*emphasis*_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Emphasis)
        self.assertEqual(ast(0)(1)(0)(0).content, "emphasis")

        ast = self.ast(u'*s_x_*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(0)(1), tree.tokens.Subscript)
        self.assertEqual(ast(0)(0)(1)(0).content, "x")

if __name__ == '__main__':
    unittest.main(verbosity=2)
