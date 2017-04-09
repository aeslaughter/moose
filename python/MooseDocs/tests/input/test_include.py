#!/usr/bin/env python
import os
import unittest
import MooseDocs
from MooseDocs.testing import MarkdownTestCase

class TestMooseIncludeMarkdown(MarkdownTestCase):
    """
    Test including markdown files.
    """
    ONE = os.path.join(MooseDocs.ROOT_DIR, 'python', 'MooseDocs', 'tests', 'input', 'one.md')
    TWO = ONE.replace('one.md', 'two.md')
    THREE = ONE.replace('one.md', 'three.md')

    def read(self, filename):
        with open(filename, 'r') as fid:
            return fid.read()

    def testInclude(self):
        md = '!include {}'.format(os.path.join('python', 'MooseDocs', 'tests', 'input', 'one.md'))
        html = self.convert(md)
        self.assertIn('Congress shall make no law', html)
        self.assertIn('A well regulated Militia', html)
        self.assertIn('No Soldier shall', html)
        self.assertNotIn('The right of the people', html)
        self.assertNotIn('!include', html)

if __name__ == '__main__':
    unittest.main(verbosity=2)
