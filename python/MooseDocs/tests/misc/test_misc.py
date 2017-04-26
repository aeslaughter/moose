#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestMisc(MarkdownTestCase):
    """
    Test that misc extension is working. command is work.
    """
    EXTENSIONS = ['MooseDocs.extensions.misc']
    def testScroll(self):
        md = 'Some before content.\n\n## One\nContent\n##Two\n\nMore Content'
        self.assertConvert('testScroll.html', md)


if __name__ == '__main__':
    unittest.main(verbosity=2)
