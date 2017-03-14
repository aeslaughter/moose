#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestMooseTable(MarkdownTestCase):
    """
    Test commands in MooseFigure extension.
    """

    def testTable(self):
        md = '!table id=table:testing caption=This is an example table with a caption.\n' \
             '| 1 | 2 |\n' \
             '|---|---|\n' \
             '| 2 | 4 |\n\n' \
             'Table \\ref{table:testing}'
        self.assertConvert('test_Table.html', md)

    def testUnknownRef(self):
        md = '\\ref{unknown}'
        self.assertConvert('test_UnknownRef.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
