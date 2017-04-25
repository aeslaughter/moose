#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestMisc(MarkdownTestCase):
    """
    Test that misc extension is working.
    """
    EXTENSIONS = ['MooseDocs.extensions.misc']
    def testCopy(self):
        md = '<pre><code>Foo</code></pre>'
        self.assertConvert('testCopy.html', md)



if __name__ == '__main__':
    unittest.main(verbosity=2)
