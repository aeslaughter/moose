#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing

class TestShortcutTokenize(testing.MarkdownTestCase):
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

        self.assertIn('key', core.SHORTCUT_DATABASE)
        self.assertString(core.SHORTCUT_DATABASE['key'], 'this is the shortcut content')

if __name__ == '__main__':
    unittest.main(verbosity=2)
