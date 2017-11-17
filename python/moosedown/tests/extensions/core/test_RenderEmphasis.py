#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderEmphasisHTML(testing.MarkdownTestCase):
    def node(self, text):
        return self.render(text)(0)(0)

    def testTree(self):
        node = self.node('*content*')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertString(node.name, 'em')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.node('*content*')
        html = node.write()
        self.assertString(html, '<em>content</em>')

class TestRenderEmphasisMaterialize(TestRenderEmphasisHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)

class TestRenderEmphasisLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render('*content*')(-1)(1)

        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.String)

        self.assertString(node.name, 'emph')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.render('*content*')(-1)(1)
        tex = self.write(node)
        self.assertString(tex, '\\emph{content}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
