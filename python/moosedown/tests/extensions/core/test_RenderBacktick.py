#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderBacktickHTML(testing.MarkdownTestCase):

    def node(self):
        return self.render('foo `code` bar')(0)

    def testTree(self):
        node = self.node()
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)
        self.assertIsInstance(node(1), tree.html.String)
        self.assertIsInstance(node(2), tree.html.Tag)
        self.assertIsInstance(node(2)(0), tree.html.String)
        self.assertIsInstance(node(3), tree.html.String)
        self.assertIsInstance(node(4), tree.html.String)

        self.assertString(node(0).content, 'foo')
        self.assertString(node(1).content, ' ')
        self.assertEqual(node(2).name, 'code')
        self.assertString(node(2)(0).content, 'code')
        self.assertString(node(3).content, ' ')
        self.assertString(node(4).content, 'bar')

    def testWrite(self):
        node = self.node()
        html = node.write()
        self.assertString(html, '<p>foo <code>code</code> bar</p>')

class TestRenderBacktickMaterialize(TestRenderBacktickHTML):

    def node(self):
        return self.render('foo `code` bar').find('body')(0)(0)

    RENDERER = MaterializeRenderer

class TestRenderBacktickLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer
    def testTree(self):
        node = self.render('foo `code` bar')(-1)
        self.assertIsInstance(node, tree.latex.Environment)
        self.assertIsInstance(node(0), tree.latex.CustomCommand)
        self.assertIsInstance(node(1), tree.latex.String)
        self.assertIsInstance(node(2), tree.latex.String)
        self.assertIsInstance(node(3), tree.latex.Command)
        self.assertIsInstance(node(4), tree.latex.String)
        self.assertIsInstance(node(5), tree.latex.String)

        self.assertString(node(0).name, 'par')
        self.assertString(node(1).content, 'foo')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).name, 'texttt')
        self.assertString(node(3)(0).content, 'code')
        self.assertString(node(4).content, ' ')
        self.assertString(node(5).content, 'bar')

    def testWrite(self):
        node = self.render('foo `code` bar')(-1)
        tex = self.write(node)
        self.assertString(tex, '\n\\begin{document}\n\\par\nfoo \\texttt{code} bar\n\\end{document}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
