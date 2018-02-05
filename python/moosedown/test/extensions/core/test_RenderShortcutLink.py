#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.common import exceptions
from moosedown.extensions import core
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderShortcutLinkHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text).find('body')(0)(0)

    def testTree(self):
        node = self.node(u'[key]\n\n[key]: content')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertEqual(node.name, 'a')
        self.assertString(node(0).content, 'key')
        self.assertEqual(node['href'], 'content')

    @mock.patch('logging.Logger.error')
    def testShortcutLinkError(self, mock):
        node = self.node(u'Some\ntext\nwith a [item] that\nis bad')
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The shortcut link key 'item' was not located", args[0])

    @mock.patch('logging.Logger.error')
    def testShortcutLinkError2(self, mock):
        node = self.node(u'[item] with some text\n[item]: foo')
        args, _ = mock.call_args
        self.assertIn("The shortcut link key 'item' was not located", args[0])

    def testWrite(self):
        node = self.node(u'[key]\n\n[key]: content')
        self.assertString(node.write(), '<a href="content">key</a>')

    def testWriteShortcutLinkWithShortcut(self):
        node = self.node(u'[test] with some text\n\n[test]: foo')
        self.assertString(node.write(), '<a href="foo">test</a>')

class TestRenderShortcutLinkMaterialize(TestRenderShortcutLinkHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)(0)

class TestRenderShortcutLinkLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'[key]\n\n[key]: content').find('document')(1)
        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.Brace)
        self.assertIsInstance(node(0)(0), tree.latex.String)
        self.assertIsInstance(node(1), tree.latex.Brace)
        self.assertIsInstance(node(1)(0), tree.latex.String)

        self.assertString(node.name, 'href')
        self.assertString(node(0)(0).content, 'content')
        self.assertString(node(1)(0).content, 'key')

    def testWrite(self):
        node = self.render(u'[key]\n\n[key]: content').find('document')(1)
        self.assertString(node.write(), '\\href{content}{key}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
