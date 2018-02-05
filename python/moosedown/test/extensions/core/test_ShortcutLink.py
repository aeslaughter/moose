#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.extensions import core
from moosedown.base import testing

class TestShortcutLinkTokenize(testing.MooseDocsTestCase):
    def testShortcutLink(self):
        link = self.ast(u'[key]\n\n[key]: content')(0)(0)
        self.assertIsInstance(link, tree.tokens.ShortcutLink)
        self.assertEqual(link.key, 'key')


if __name__ == '__main__':
    unittest.main(verbosity=2)
