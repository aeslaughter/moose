#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing

class TestShortcutLinkTokenize(testing.MarkdownTestCase):
    """
    Test shortcuts:

    [link]: something or another
    """
    def setUp(self):
        testing.MarkdownTestCase.setUp(self)
        core.SHORTCUT_DATABASE = dict(key='content')

    def testShortcutLink(self):
        link = self.ast('[key]')(0)(0)
        self.assertIsInstance(link, tree.tokens.ShortcutLink)
        self.assertEqual(link.key, 'key')


if __name__ == '__main__':
    unittest.main(verbosity=2)
