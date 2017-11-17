#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestHeadingHashHTML(testing.MarkdownTestCase):
    def node(self, text):
        return self.render(text)(0)

    def testBasic(self):
        h = self.node('# Heading with Spaces')
        self.assertIsInstance(h, tree.html.Tag)
        self.assertEqual(h.name, 'h1')
        for child in h.children:
            self.assertIsInstance(child, tree.html.String)
        self.assertEqual(h(0).content, 'Heading')
        self.assertEqual(h(1).content, ' ')
        self.assertEqual(h(2).content, 'with')
        self.assertEqual(h(3).content, ' ')
        self.assertEqual(h(4).content, 'Spaces')

        self.assertString(h.write(), "<h1>Heading with Spaces</h1>")

    def testSettings(self):
        h = self.node('# Heading with Spaces style=font-size:42pt;')
        self.assertIsInstance(h, tree.html.Tag)
        self.assertEqual(h.name, 'h1')
        for child in h.children:
            self.assertIsInstance(child, tree.html.String)
        self.assertEqual(h(0).content, 'Heading')
        self.assertEqual(h(1).content, ' ')
        self.assertEqual(h(2).content, 'with')
        self.assertEqual(h(3).content, ' ')
        self.assertEqual(h(4).content, 'Spaces')
        self.assertEqual(h['style'], 'font-size:42pt;')

        self.assertString(h.write(), '<h1 style="font-size:42pt;">Heading with Spaces</h1>')

class TestHeadingHashMaterialize(TestHeadingHashHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)

class TestHeadingHashLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer


    def checkLevel(self, lvl, cmd):
        node = self.render('{} Heading with Space'.format('#'*lvl))(-1)(0)
        self.assertIsInstance(node, tree.latex.Command)
        self.assertString(node.name, cmd)

        self.assertIsInstance(node(0), tree.latex.Command)
        self.assertString(node(0).name, 'label')
        self.assertString(node(0)(0).content, 'heading-with-space')

        self.assertIsInstance(node(1), tree.latex.String)
        self.assertIsInstance(node(2), tree.latex.String)
        self.assertIsInstance(node(3), tree.latex.String)
        self.assertIsInstance(node(4), tree.latex.String)
        self.assertIsInstance(node(5), tree.latex.String)

       # self.assertString(node(0).name, 'par')
        self.assertString(node(1).content, 'Heading')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).content, 'with')
        self.assertString(node(4).content, ' ')
        self.assertString(node(5).content, 'Space')

        tex = self.write(node)
        self.assertString(tex, '\n\\%s{\\label{heading-with-space}Heading with Space}\n' % cmd)

    def testLevels(self):
        self.checkLevel(1, 'chapter')
        self.checkLevel(2, 'section')
        self.checkLevel(3, 'subsection')
        self.checkLevel(4, 'subsubsection')
        self.checkLevel(5, 'paragraph')
        self.checkLevel(6, 'subparagraph')


if __name__ == '__main__':
    unittest.main(verbosity=2)
