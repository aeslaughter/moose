#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing

class TestShortcutTokenize(testing.MooseDocsTestCase):
    def testShortcut(self):
        shortcut = self.ast(u'[key]: this is the shortcut content')(0)
        self.assertIsInstance(shortcut, tree.tokens.Shortcut)
        self.assertEqual(shortcut.key, 'key')
        self.assertEqual(shortcut.link, 'this is the shortcut content')

if __name__ == '__main__':
    unittest.main(verbosity=2)
