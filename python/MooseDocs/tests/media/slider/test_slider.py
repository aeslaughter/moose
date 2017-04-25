#!/usr/bin/env python
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestSlider(MarkdownTestCase):
    """
    Test to make sure that "moose/python/MooseDocs/extensions/MooseSlider.py"
    parses a test block correctly.
    """
    EXTENSIONS = ['MooseDocs.extensions.media']
    def testDefault(self):
        self.assertConvertFile('testDefault.html', 'testDefault.md')

    def testDefaultId(self):
        self.assertConvertFile('testDefaultId.html', 'testDefaultId.md')

if __name__ == '__main__':
    unittest.main(verbosity=2)
