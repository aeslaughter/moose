#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderShortcutLinkHTML(testing.MarkdownTestCase):
    """
    Test Lines: [link](bar.html foo=bar)
    """
    def node(self, text):
        return self.render(text).find('body')(0)(0)

    def setUp(self):
        testing.MarkdownTestCase.setUp(self)
        core.SHORTCUT_DATABASE = dict(key='content')

    def testTree(self):
        node = self.node('[key]')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)

        self.assertEqual(node.name, 'a')
        self.assertString(node(0).content, 'key')
        self.assertEqual(node['href'], 'content')

    @mock.patch('logging.Logger.error')
    def testShortcutLinkError(self, mock):
        self.node('Some\ntext\nwith a [item] that\nis bad')
        mock.assert_called_once()
        args, kwargs = mock.call_args
        self.assertIn("The shortcut link key '%s' was not located", args[0])

    @mock.patch('logging.Logger.error')
    def testShortcutLinkError2(self, mock):
        """
        Test missing link when two empty lines are not used prior to shortcut definitions
        """
        node = self.render('[item] with some text\n[item]: foo')
        mock.assert_called()
        args, kwargs = mock.call_args
        self.assertIn("The shortcut link key '%s' was not located", args[0])

    def testWrite(self):
        node = self.node('[key]')
        html = self.write(node)
        self.assertString(html, '<a href="content">key</a>')

    def testWriteShortcutLinkWithShortcut(self):
        node = self.node('[test] with some text\n\n[test]: foo')
        html = self.write(node)
        self.assertString(html, '<a href="foo">test</a>')

class TestRenderShortcutLinkMaterialize(TestRenderShortcutLinkHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(-1)(0)(0)

class TestRenderShortcutLinkLatex(testing.MarkdownTestCase):
    RENDERER = LatexRenderer

    def setUp(self):
        testing.MarkdownTestCase.setUp(self)
        core.SHORTCUT_DATABASE = dict(key='content')

    def testTree(self):
        node = self.render('[key]').find('document')(1)
        self.assertIsInstance(node, tree.latex.Command)
        self.assertIsInstance(node(0), tree.latex.Brace)
        self.assertIsInstance(node(0)(0), tree.latex.String)
        self.assertIsInstance(node(1), tree.latex.Brace)
        self.assertIsInstance(node(1)(0), tree.latex.String)

        self.assertString(node.name, 'href')
        self.assertString(node(0)(0).content, 'content')
        self.assertString(node(1)(0).content, 'key')

    def testWrite(self):
        node = self.render('[key]').find('document')(1)
        tex = self.write(node)
        self.assertString(tex, '\\href{content}{key}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
