#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderStringHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text).find('body')(0)

    def testTree(self):
        node = self.node(u'sit amet, consectetur')
        self.assertIsInstance(node, tree.html.Tag)
        for i in range(6):
            self.assertIsInstance(node(i), tree.html.String)

        self.assertString(node(0).content, 'sit')
        self.assertString(node(1).content, ' ')
        self.assertString(node(2).content, 'amet')
        self.assertString(node(3).content, ',')
        self.assertString(node(4).content, ' ')
        self.assertString(node(5).content, 'consectetur')

    def testWrite(self):
        node = self.node(u'sit amet, consectetur')
        self.assertString(node.write(), '<p>sit amet, consectetur</p>')

class TestRenderStringMaterialize(TestRenderStringHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)

class TestRenderStringLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'sit amet, consectetur').find('document')
        for i in range(1,7):
            self.assertIsInstance(node(i), tree.latex.String)

        self.assertString(node(1).content, 'sit')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).content, 'amet')
        self.assertString(node(4).content, ',')
        self.assertString(node(5).content, ' ')
        self.assertString(node(6).content, 'consectetur')

    def testWrite(self):
        node = self.render(u'sit amet, consectetur').find('document')
        self.assertString(node.write(), '\n\\begin{document}\n\n\\par\nsit amet, consectetur\n\\end{document}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
