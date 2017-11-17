#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderFormatHTML(testing.MarkdownTestCase):
    def node(self, text):
        return self.render(text)(0)(0)

    def checkItem(self, char, tag):
        if isinstance(char, str):
            char = (char, char)
        node = self.node('{}content{}'.format(*char))
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertString(node.name, tag)
        self.assertString(node(0).content, 'content')

        html = node.write()
        self.assertString(html, '<{0}>content</{0}>'.format(tag))


    def testSuperscript(self):
        self.checkItem(('^{', '}'), 'sup')

    def testSubscript(self):
        self.checkItem(('_{', '}'), 'sub')

class TestRenderFormatMaterialize(TestRenderFormatHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)

class TestRenderFormatLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer

    def checkItem(self, char, cmd):
        node = self.render('{0}content{0}'.format(char))(-1)(1)

        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.String)

        self.assertString(node.name, cmd)
        self.assertString(node(0).content, 'content')

        tex = self.write(node)
        self.assertString(tex, '\\%s{content}' % cmd)

    def testStrong(self):
        self.checkItem('+', 'textbf')

    def testUnderline(self):
        self.checkItem('=', 'underline')

    def testEmphasis(self):
        self.checkItem('*', 'emph')

    def testStrike(self):
        self.checkItem('~', 'sout')

    def testSuperscript(self):
        self.checkSubSuperscript('^')

    def testSubscript(self):
        self.checkSubSuperscript('_')

    def checkSubSuperscript(self, key):
        node = self.render('foo%s{content}' % key)(-1)

        self.assertIsInstance(node(1), tree.latex.String)
        self.assertString(node(1).content, 'foo')

        self.assertIsInstance(node(2), tree.latex.InlineMath)
        self.assertString(node(2)(0).content, '%s{' % key)

        self.assertIsInstance(node(2)(1), tree.latex.Command)
        self.assertString(node(2)(1).name, 'text')
        self.assertString(node(2)(1)(0).content, 'content')

        self.assertString(node(2)(2).content, '}')

        tex = self.write(node(2))
        self.assertString(tex, '$\%s\{\\text{content}\}$' % key)

if __name__ == '__main__':
    unittest.main(verbosity=2)
