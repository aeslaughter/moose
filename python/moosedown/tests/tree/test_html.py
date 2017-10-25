#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown.tree import html


class TestHTML(unittest.TestCase):
    """
    Tests for html tree structure.
    """
    def testTag(self):
        tag = html.Tag('section')
        self.assertEqual(tag.write(), '<section></section>')

    def testString(self):
        tag = html.String(content='section')
        self.assertEqual(tag.write(), 'section')

        tag = html.String(content='<section>', escape=True)
        self.assertEqual(tag.write(), '&lt;section&gt;')

    def testTagString(self):
        tag = html.Tag('h1')
        html.String(content='foo', parent=tag)
        self.assertEqual(tag.write(), '<h1>foo</h1>')

if __name__ == '__main__':
    unittest.main(verbosity=2)
