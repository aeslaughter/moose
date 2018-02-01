#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderQuoteHTML(testing.MooseDocsTestCase):
    """
    Test Lines: [link](bar.html foo=bar)
    """
    def node(self, text):
        return self.render(text)(0)

    def testTree(self):
        node = self.node(u'> foo bar')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertEqual(node.name, 'blockquote')
        self.assertIsInstance(node(0), tree.html.Tag)
        self.assertString(node(0).name, 'p')

        self.assertIsInstance(node(0)(0), tree.html.String)
        self.assertString(node(0)(0).content, 'foo')

        self.assertIsInstance(node(0)(1), tree.html.String)
        self.assertString(node(0)(1).content, ' ')

        self.assertIsInstance(node(0)(2), tree.html.String)
        self.assertString(node(0)(2).content, 'bar')

    def testWrite(self):
        node = self.node(u'> foo bar')
        html = self.write(node)
        self.assertString(html, '<blockquote><p>foo bar</p></blockquote>')

class TestRenderQuoteMaterialize(TestRenderQuoteHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)

class TestRenderQuoteLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'> foo bar').find('document')(-1)
        self.assertIsInstance(node, tree.latex.Environment)
        self.assertString(node.name, 'quote')

        self.assertIsInstance(node(0), tree.latex.Command)
        self.assertString(node(0).name, 'par')

        self.assertIsInstance(node(1), tree.latex.String)
        self.assertIsInstance(node(2), tree.latex.String)
        self.assertIsInstance(node(3), tree.latex.String)

        self.assertString(node(1).content, 'foo')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).content, 'bar')


    def testWrite(self):
        node = self.render(u'> foo bar').find('document')(-1)
        tex = self.write(node).strip('\n')
        self.assertString(tex, '\\begin{quote}\n\\par\nfoo bar\n\\end{quote}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
