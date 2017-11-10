#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing

class TestShortcut(testing.MarkdownTestCase):
    """
    Test shortcuts:

    [link]: something or another
    """
    def setUp(self):
        testing.MarkdownTestCase.setUp(self)
        core.SHORTCUT_DATABASE = dict()

    def testShortcut(self):
        shortcut = self.ast('[key]: this is the shortcut content')(0)
        self.assertIsInstance(shortcut, tree.tokens.Shortcut)
        self.assertEqual(shortcut.key, 'key')
        self.assertEqual(shortcut.content, 'this is the shortcut content')

        # Should not produce any html
        html = self.html(shortcut)
        self.assertEqual(html.write(), '<body></body>')

    def testShortcutLink(self):
        link = self.ast('[key]')(0)(0)
        self.assertIsInstance(link, tree.tokens.ShortcutLink)
        self.assertEqual(link.key, 'key')

    @mock.patch('logging.Logger.error')
    def testShortcutLinkError(self, mock):
        link = self.ast('Some\ntext\nwith a [key] that\nis bad')
        html = self.html(link)
        mock.assert_called_once()
        args, kwargs = mock.call_args
        self.assertIn("The shortcut link key '%s' was not located", args[0])

    @mock.patch('logging.Logger.error')
    def testShortcutLinkError2(self, mock):
        """
        Test missing link when two empty lines are not used prior to shortcut definitions
        """
        link = self.ast('[key] with some text\n[key]: foo')
        html = self.html(link)
        mock.assert_called()
        args, kwargs = mock.call_args
        self.assertIn("The shortcut link key '%s' was not located", args[0])

    def testShortcutWithLink(self):
        link = self.ast('[key] with some text\n\n[key]: foo')
        html = self.html(link)
        gold = '<body><p><a href="foo">key</a> with some text</p></body>'
        self.assertString(html.write(), gold)

if __name__ == '__main__':
    unittest.main(verbosity=2)
