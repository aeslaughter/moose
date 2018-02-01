#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestLinkTokenize(testing.MooseDocsTestCase):
    """
    Test Lines: [link](bar.html foo=bar)
    """
    def testBasic(self):
        link = self.ast('[link](url.html)')(0)(0)
        self.assertIsInstance(link.parent, tree.tokens.Paragraph)
        self.assertIsInstance(link, tree.tokens.Link)
        self.assertIsInstance(link(0), tree.tokens.Word)
        self.assertEqual(link(0).content, 'link')
        self.assertEqual(link.url, 'url.html')

    def testSettings(self):
        link = self.ast('[link](url.html id=bar)')(0)(0)
        self.assertEqual(link['id'], 'bar')

if __name__ == '__main__':
    unittest.main(verbosity=2)
