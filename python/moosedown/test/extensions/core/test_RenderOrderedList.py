#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderOrderedListHTML(testing.MooseDocsTestCase):
    def node(self, text):
        root = self.render(text)
        return root(0)

    def testTree(self):
        node = self.node(u'1. foo\n1. bar')

        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.Tag)
        self.assertIsInstance(node(1), tree.html.Tag)

        self.assertIsInstance(node(0)(0), tree.html.Tag)
        self.assertIsInstance(node(1)(0), tree.html.Tag)

        self.assertIsInstance(node(0)(0)(0), tree.html.String)
        self.assertIsInstance(node(1)(0)(0), tree.html.String)

        self.assertString(node.name, 'ol')
        self.assertString(node(0).name, 'li')
        self.assertString(node(1).name, 'li')

        self.assertString(node(0)(0).name, 'p')
        self.assertString(node(1)(0).name, 'p')

        self.assertString(node(0)(0)(0).content, 'foo')
        self.assertString(node(1)(0)(0).content, 'bar')

    def testWrite(self):
        node = self.node(u'1. foo\n1. bar')
        html = node.write()
        self.assertString(html, '<ol><li><p>foo </p></li><li><p>bar</p></li></ol>')

class TestRenderOrderedListMaterialize(TestRenderOrderedListHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)

    def testWrite(self):
        node = self.node(u'1. foo\n1. bar')
        html = node.write()
        self.assertString(html,
                          '<ol start="1" class="browser-default"><li><p>foo </p></li><li><p>bar</p></li></ol>')

class TestRenderOrderedListLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'1. foo\n1. bar')(-1)(0)
        self.assertIsInstance(node, tree.latex.Environment)
        self.assertIsInstance(node(0), tree.latex.CustomCommand)
        self.assertIsInstance(node(1), tree.latex.Command)
        self.assertIsInstance(node(2), tree.latex.String)
        self.assertIsInstance(node(3), tree.latex.String)
        self.assertIsInstance(node(4), tree.latex.CustomCommand)
        self.assertIsInstance(node(5), tree.latex.Command)
        self.assertIsInstance(node(6), tree.latex.String)

        self.assertString(node.name, 'enumerate')
        self.assertString(node(0).name, 'item')
        self.assertString(node(1).name, 'par')
        self.assertString(node(2).content, 'foo')
        self.assertString(node(3).content, ' ')
        self.assertString(node(4).name, 'item')
        self.assertString(node(5).name, 'par')
        self.assertString(node(6).content, 'bar')

    def testWrite(self):
        node = self.render(u'1. foo\n1. bar')(-1)(0)
        tex = node.write()
        self.assertString(tex,
                          '\n\\begin{enumerate}\n\n\\item\n\\par\nfoo \n\\item\n\\par\nbar\n\\end{enumerate}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
