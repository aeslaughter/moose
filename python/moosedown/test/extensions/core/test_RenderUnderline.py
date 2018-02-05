#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderUnderlineHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text)(0)(0)

    def testTree(self):
        node = self.node(u'=content=')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertString(node.name, 'u')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.node(u'=content=')
        self.assertString(node.write(), '<u>content</u>')

class TestRenderUnderlineMaterialize(TestRenderUnderlineHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)(0)

class TestRenderUnderlineLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'=content=').find('document')(1)

        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.String)

        self.assertString(node.name, 'underline')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.render(u'=content=').find('document')(1)
        self.assertString(node.write(), '\\underline{content}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
