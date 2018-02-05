#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderLinkHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text)(0)(0)

    def testTree(self):
        node = self.node(u'[link](url.html)')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertEqual(node.name, 'a')
        self.assertIsInstance(node(0), tree.html.String)
        self.assertString(node(0).content, 'link')
        self.assertString(node['href'], 'url.html')

    def testTreeSettings(self):
        node = self.node(u'[link](url.html id=foo)')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertEqual(node.name, 'a')
        self.assertIsInstance(node(0), tree.html.String)
        self.assertString(node(0).content, 'link')
        self.assertString(node['href'], 'url.html')
        self.assertString(node['id'], 'foo')

    def testWrite(self):
        link = self.node(u'[link](url.html)')
        self.assertString(link.write(), '<a href="url.html">link</a>')

    def testWriteSettings(self):
        link = self.node(u'[link](url.html id=bar)')
        self.assertString(link.write(), '<a href="url.html" id="bar">link</a>')

class TestRenderLinkMaterialize(TestRenderLinkHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)(0)

class TestRenderLinkLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'[link](url.html)')(-1)(1)
        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.Brace)
        self.assertIsInstance(node(0)(0), tree.latex.String)
        self.assertIsInstance(node(1), tree.latex.Brace)
        self.assertIsInstance(node(1)(0), tree.latex.String)

        self.assertString(node.name, 'href')
        self.assertString(node(0)(0).content, 'url.html')
        self.assertString(node(1)(0).content, 'link')

    def testWrite(self):
        node = self.render(u'[link](url.html)')(-1)(1)
        self.assertString(node.write(), '\\href{url.html}{link}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
