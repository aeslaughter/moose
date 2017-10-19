#!/usr/bin/env python
import unittest
import logging
import mock

from mooseutils import text_diff

from moosedown import MooseMarkdown
from moosedown import tree

class TestFormat(unittest.TestCase):
    """
    Test inline formatting (e.g., *bold*, _italic_, etc.)
    """
    def setUp(self):
        self._markdown = MooseMarkdown.MooseMarkdown(materialize=False)

    def ast(self, md):
        return self._markdown.ast(md)

    def html(self, ast):
        return self._markdown.renderer.render(ast)

    def assertHTML(self, ast, gold):
        html = self.html(ast).write()
        self.assertEqual(html, gold, text_diff(html, gold))

    def testStrong(self):
        ast = self.ast('+strong+')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")

        self.assertHTML(ast, '<body><p><strong>strong</strong></p></body>')

        ast = self.ast('+strong with space\nand a new line+')
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
        ast = self.ast('*emphasis*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")

        ast = self.ast('*emphasis with space\nand a new line*')
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

    def testSuperscriptAndSubscript(self):
        ast = self.ast('s_{y^{x}}')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

        ast = self.ast('s^{y^{x}}')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

        ast = self.ast('s^{y_{x}}')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tree.tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

    def testNesting(self):
        ast = self.ast('=*emphasis* underline=')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Emphasis)
        self.assertEqual(ast(0)(0)(0)(0).content, "emphasis")
        self.assertIsInstance(ast(0)(0)(2), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "underline")

        ast = self.ast('*=underline= emphasis*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Underline)
        self.assertEqual(ast(0)(0)(0)(0).content, "underline")
        self.assertIsInstance(ast(0)(0)(2), tree.tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "emphasis")

        ast = self.ast('*=+~strike~ bold+ under= emphasis*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0)(0), tree.tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0)(0)(0), tree.tokens.Strikethrough)

        ast = self.ast('s_{*emphasis*}')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(1), tree.tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tree.tokens.Emphasis)
        self.assertEqual(ast(0)(1)(0)(0).content, "emphasis")

        ast = self.ast('*s_{x}*')
        self.assertIsInstance(ast(0), tree.tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tree.tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tree.tokens.Word)
        self.assertIsInstance(ast(0)(0)(1), tree.tokens.Subscript)
        self.assertEqual(ast(0)(0)(1)(0).content, "x")





if __name__ == '__main__':
    unittest.main(verbosity=2)
