#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestMisc(MarkdownTestCase):
    """
    Test that misc extension is working. command is work.
    """
    EXTENSIONS = ['MooseDocs.extensions.misc']
    def testCopy(self):
        md = '<pre><code>Foo</code></pre>'
        self.assertConvert('testCopy.html', md)

    def testScroll(self):
        md = '<div id=moose-markdown-content><h2>One</h2><p>Content</p><h2>Two</h2><p>More Content</p></div>'
        self.assertConvert('testScroll.html', md)


if __name__ == '__main__':
    unittest.main(verbosity=2)
