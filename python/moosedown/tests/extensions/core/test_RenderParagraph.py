#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderParagraphHTML(testing.MarkdownTestCase):
    """
    Test Lines: [link](bar.html foo=bar)
    """
    def node(self, text):
        return self.render(text).find('body')

    def testTree(self):
        node = self.node('foo\n\n\n\nbar')
        self.assertIsInstance(node, tree.html.Tag)

        self.assertIsInstance(node(0), tree.html.Tag)
        self.assertEqual(node(0).name, 'p')
        self.assertIsInstance(node(0)(0), tree.html.String)
        self.assertString(node(0)(0).content, 'foo')

        self.assertIsInstance(node(1), tree.html.Tag)
        self.assertEqual(node(1).name, 'p')
        self.assertIsInstance(node(1)(0), tree.html.String)
        self.assertString(node(1)(0).content, 'bar')

    def testWrite(self):
        node = self.node('foo\n\n\n\nbar')
        html = self.write(node(0))
        self.assertString(html, '<p>foo</p>')
        html = self.write(node(1))
        self.assertString(html, '<p>bar</p>')

class TestRenderParagraphMaterialize(TestRenderParagraphHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(-1)

class TestRenderParagraphLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render('[link](url.html)')(-1)(1)
        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.Brace)
        self.assertIsInstance(node(0)(0), tree.latex.String)
        self.assertIsInstance(node(1), tree.latex.Brace)
        self.assertIsInstance(node(1)(0), tree.latex.String)

        self.assertString(node.name, 'href')
        self.assertString(node(0)(0).content, 'url.html')
        self.assertString(node(1)(0).content, 'link')

    def testWrite(self):
        node = self.render('+content+')(-1)(1)
        tex = self.write(node)
        self.assertString(tex, '\\textbf{content}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
