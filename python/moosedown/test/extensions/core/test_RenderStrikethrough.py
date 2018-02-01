#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderStrikethroughHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text)(0)(0)

    def testTree(self):
        node = self.node(u'~content~')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertString(node.name, 'strike')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.node(u'~content~')
        html = node.write()
        self.assertString(html, '<strike>content</strike>')

class TestRenderStrikethroughMaterialize(TestRenderStrikethroughHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)

class TestRenderStrikethroughLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'~content~')(-1)(1)

        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.String)

        self.assertString(node.name, 'sout')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.render(u'~content~')(-1)(1)
        tex = self.write(node)
        self.assertString(tex, '\\sout{content}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
