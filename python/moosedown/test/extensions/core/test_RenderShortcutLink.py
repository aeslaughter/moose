#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderShortcutLinkHTML(testing.MooseDocsTestCase):
    """
    Test Lines: [link](bar.html foo=bar)
    """
    def node(self, text):
        return self.render(text).find('body')(0)(0)

    def setUp(self):
        testing.MooseDocsTestCase.setUp(self)
        core.SHORTCUT_DATABASE = dict(key='content')

    def testTree(self):
        node = self.node(u'[key]')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertEqual(node.name, 'a')
        self.assertString(node(0).content, 'key')
        self.assertEqual(node['href'], 'content')

    def testShortcutLinkError(self):
        with self.assertRaises(KeyError) as e:
            self.node(u'Some\ntext\nwith a [item] that\nis bad')
        self.assertIn("The shortcut link key 'item' was not located", e.exception.message)

    def testShortcutLinkError2(self):
        """
        Test missing link when two empty lines are not used prior to shortcut definitions
        """
        with self.assertRaises(KeyError) as e:
            node = self.render(u'[item] with some text\n[item]: foo')
        self.assertIn("The shortcut link key 'item' was not located", e.exception.message)

    def testWrite(self):
        node = self.node(u'[key]')
        html = self.write(node)
        self.assertString(html, '<a href="content">key</a>')

    def testWriteShortcutLinkWithShortcut(self):
        node = self.node(u'[test] with some text\n\n[test]: foo')
        html = self.write(node)
        self.assertString(html, '<a href="foo">test</a>')

class TestRenderShortcutLinkMaterialize(TestRenderShortcutLinkHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(-1)(0)(0)

class TestRenderShortcutLinkLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def setUp(self):
        testing.MooseDocsTestCase.setUp(self)
        core.SHORTCUT_DATABASE = dict(key='content')

    def testTree(self):
        node = self.render(u'[key]').find('document')(1)
        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.Brace)
        self.assertIsInstance(node(0)(0), tree.latex.String)
        self.assertIsInstance(node(1), tree.latex.Brace)
        self.assertIsInstance(node(1)(0), tree.latex.String)

        self.assertString(node.name, 'href')
        self.assertString(node(0)(0).content, 'content')
        self.assertString(node(1)(0).content, 'key')

    def testWrite(self):
        node = self.render(u'[key]').find('document')(1)
        tex = self.write(node)
        self.assertString(tex, '\\href{content}{key}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
