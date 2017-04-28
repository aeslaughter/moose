#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestRef(MarkdownTestCase):
    """
    Test that misc extension is working. command is work.
    """
    EXTENSIONS = ['MooseDocs.extensions.refs', 'MooseDocs.extensions.listings']
    def testRef(self):
        md = '!listing id=foo\n```testing```\n\n\\ref{foo}'
        self.assertConvert('testRef.html', md)

    def testUnknownRef(self):
        md = '\\ref{unknown}'
        self.assertConvert('testUnknownRef.html', md)


if __name__ == '__main__':
    unittest.main(verbosity=2)
