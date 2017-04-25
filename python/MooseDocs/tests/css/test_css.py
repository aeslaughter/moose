#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestCSS(MarkdownTestCase):
    """
    Test that !css command is work.
    """
    EXTENSIONS = ['MooseDocs.extensions.css']
    def testCSS(self):
        self.assertConvertFile('test_css.html', os.path.join(self.WORKING_DIR, 'css.md'))

    def testCSSList(self):
        self.assertConvertFile('test_css_list.html', os.path.join(self.WORKING_DIR, 'css_list.md'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
