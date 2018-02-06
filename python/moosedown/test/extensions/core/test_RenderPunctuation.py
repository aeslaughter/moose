#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderPunctuationHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text).find('body')(0)

    def testTree(self):
        node = self.node(u'foo-bar')
        self.assertString(node(0).content, 'foo')
        self.assertString(node(1).content, '-')
        self.assertString(node(2).content, 'bar')

        node = self.node(u'foo--bar')
        self.assertString(node(1).content, '&ndash;')

        node = self.node(u'foo---bar')
        self.assertString(node(1).content, '&mdash;')

    def testWrite(self):
        node = self.node(u'foo-bar')
        self.assertString(node.write(), '<p>foo-bar</p>')

class TestRenderPunctuationMaterialize(TestRenderPunctuationHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)

class TestRenderPunctuationLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'foo-bar').find('document')
        self.assertString(node(1).content, 'foo')
        self.assertString(node(2).content, '-')
        self.assertString(node(3).content, 'bar')

    def testWrite(self):
        node = self.render(u'foo-bar').find('document')
        self.assertString(node.write(), '\n\\begin{document}\n\n\\par\nfoo-bar\n\\end{document}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
