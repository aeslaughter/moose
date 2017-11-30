#!/usr/bin/env python
import unittest
import os

from moosedown import ROOT_DIR
from moosedown.tree import page


class TestPage(unittest.TestCase):
    """
    Tests for latex tree structure.
    """
    def testPageNodeBase(self):
        one = page.PageNodeBase(name='one', source='foo')
        two = page.PageNodeBase(one, name='two')
        three = page.PageNodeBase(two, name='three')

        self.assertEqual(one.source, 'foo')
        self.assertEqual(one.local, 'one')
        self.assertEqual(two.local, 'one/two')
        self.assertEqual(three.local, 'one/two/three')

    def testDirectoryNode(self):
        node = page.DirectoryNode(source='foo')
        self.assertEqual(node.source, 'foo')
        self.assertEqual(node.COLOR, 'CYAN')

    def testFileNode(self):
        source = os.path.join(ROOT_DIR, 'docs', 'content', 'utilities', 'moosedown', 'index.md')
        node = page.FileNode(source=source)
        self.assertEqual(node.source, source)
        self.assertIn('# MOOSE Markdown Specification (MooseDown)', node.content)

if __name__ == '__main__':
    unittest.main(verbosity=2)
