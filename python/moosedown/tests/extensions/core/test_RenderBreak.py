#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderBreakHTML(testing.MarkdownTestCase):
    def testBasic(self):
        node = self.html('foo\nbar')(0)
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)
        self.assertIsInstance(node(1), tree.html.String)
        self.assertIsInstance(node(2), tree.html.String)

        self.assertString(node(0).content, 'foo')
        self.assertString(node(1).content, ' ')
        self.assertString(node(2).content, 'bar')

    def testWrite(self):
        node = self.render('foo\nbar')(0)
        html = node.write()
        self.assertString(html, '<p>foo bar</p>')

class TestRenderBreakMaterialize(TestRenderBreakHTML):
    RENDERER = MaterializeRenderer

class TestRenderBreakMaterialize(TestRenderBreakHTML):
    RENDERER = LatexRenderer
    def testBasic(self):
        node = self.html('foo\nbar')(-1)
        self.assertIsInstance(node, tree.latex.Environment)
        self.assertIsInstance(node(0), tree.latex.CustomCommand)
        self.assertIsInstance(node(1), tree.latex.String)
        self.assertIsInstance(node(2), tree.latex.String)
        self.assertIsInstance(node(3), tree.latex.String)

        self.assertString(node(0)._command, 'par')
        self.assertString(node(1).content, 'foo')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).content, 'bar')

    def testWrite(self):
        node = self.render('foo\nbar')(-1)
        tex = self.write(node)
        self.assertString(tex, '\begin{document}\parfoo bar\n\end{document}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
