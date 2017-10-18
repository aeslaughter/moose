#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import MooseMarkdown
from moosedown import tree

class TestFormat(unittest.TestCase):
    """
    Test inline formatting (e.g., *bold*, _italic_, etc.)
    """

    def ast(self, md):
        markdown = MooseMarkdown.MooseMarkdown(materialize=False)
        return markdown.ast(md)

    def html(self, md):
        markdown = MooseMarkdown.MooseMarkdown(materialize=False)
        return markdown.convert(md)

    def testStrong(self):
        ast = self.ast('*strong*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")

        ast = self.ast('*strong with space\nand a new line*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testUnderline(self):
        ast = self.ast('=underline=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "underline")

        ast = self.ast('=underline with space\nand a new line=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "underline")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testEmphasis(self):
        ast = self.ast('_emphasis_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")

        ast = self.ast('_emphasis with space\nand a new line_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testStrikethrough(self):
        ast = self.ast('~strikethrough~')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strikethrough)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strikethrough")

        ast = self.ast('~strikethrough with space\nand a new line~')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strikethrough)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strikethrough")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testSubscript(self):
        ast = self.ast('S_{x}')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(0).content, "x")

    def testSuperscript(self):
        ast = self.ast('S^{x}')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(0).content, "x")

    def testNesting(self):
        ast = self.ast('=_emphasis_ underline=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Emphasis)
        self.assertEqual(ast(0)(0)(0)(0).content, "emphasis")
        self.assertIsInstance(ast(0)(0)(2), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "underline")

        ast = self.ast('_=underline= emphasis_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Underline)
        self.assertEqual(ast(0)(0)(0)(0).content, "underline")
        self.assertIsInstance(ast(0)(0)(2), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "emphasis")

        ast = self.ast('_=*~strike~ bold* under= emphasis_')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0)(0)(0), tree.tokens.Strikethrough)





if __name__ == '__main__':
    unittest.main(verbosity=2)
