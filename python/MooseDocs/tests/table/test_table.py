#!/usr/bin/env python
import os
import unittest
import MooseDocs
from MooseDocs.testing import MarkdownTestCase

class TestMooseTable(MarkdownTestCase):
    """
    Test commands in MooseFigure extension.
    """
    EXTENSIONS=['MooseDocs.extensions.tables', 'MooseDocs.extensions.refs']

    def testTable(self):
        md = '!table caption=This is an example table with a caption.\n' \
             '| 1 | 2 |\n' \
             '|---|---|\n' \
             '| 2 | 4 |\n\n'
        self.assertConvert('testTable.html', md)

    def testTableId(self):
        md = '!table id=table:foo caption=This is an example table with a caption.\n' \
             '| 1 | 2 |\n' \
             '|---|---|\n' \
             '| 2 | 4 |\n\n'
        self.assertConvert('testTableId.html', md)

    def testTableRef(self):
        md = '!table id=foo caption=This is an example table with a caption.\n' \
             '| 1 | 2 |\n' \
             '|---|---|\n' \
             '| 2 | 4 |\n\n' \
             '\\ref{foo}'
        self.assertConvert('testTableRef.html', md)


    #def testUnknownRef(self):
    #    md = '\\ref{unknown}'
    #    self.assertConvert('test_UnknownRef.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
