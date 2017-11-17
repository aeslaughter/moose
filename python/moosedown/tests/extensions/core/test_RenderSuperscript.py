#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderSuperscriptHTML(testing.MarkdownTestCase):
    def node(self, text):
        return self.render(text)(0)(0)

    def testTree(self):
        node = self.node('^{content}')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertString(node.name, 'sup')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.node('^{content}')
        html = node.write()
        self.assertString(html, '<sup>content</sup>')

class TestRenderSuperscriptMaterialize(TestRenderSuperscriptHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)

class TestRenderSuperscriptLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render('foo^{content}')(-1)

        self.assertIsInstance(node(1), tree.latex.String)
        self.assertString(node(1).content, 'foo')

        self.assertIsInstance(node(2), tree.latex.InlineMath)
        self.assertString(node(2)(0).content, '^{')

        self.assertIsInstance(node(2)(1), tree.latex.Command)
        self.assertString(node(2)(1).name, 'text')
        self.assertString(node(2)(1)(0).content, 'content')

        self.assertString(node(2)(2).content, '}')

    def testWrite(self):
        node = self.render('foo^{content}')(-1)
        tex = self.write(node(2))
        self.assertString(tex, '$\^\{\\text{content}\}$')

if __name__ == '__main__':
    unittest.main(verbosity=2)
