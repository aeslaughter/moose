#!/usr/bin/env python
import unittest
import os

from MooseDocs import ROOT_DIR
from moosedown.tree import page


class TestPage(unittest.TestCase):
    """
    Tests for latex tree structure.
    """
    def testPageNodeBase(self):
        one = page.PageNodeBase(name='one', content=u'foo')
        two = page.PageNodeBase(one, name='two')
        three = page.PageNodeBase(two, name='three')

    def testLocationNodeBase(self):
        one = page.LocationNodeBase(source='one')
        two = page.LocationNodeBase(one, source='foo/two')
        three = page.LocationNodeBase(two, source='foo/bar/three')

        self.assertEqual(one.source, 'one')
        self.assertEqual(one.local, 'one')
        self.assertEqual(one.name, 'one')

        self.assertEqual(two.source, 'foo/two')
        self.assertEqual(two.local, 'one/two')
        self.assertEqual(two.name, 'two')

        self.assertEqual(three.source, 'foo/bar/three')
        self.assertEqual(three.local, 'one/two/three')
        self.assertEqual(three.name, 'three')

    def testDirectoryNode(self):
        node = page.DirectoryNode(source='foo')
        self.assertEqual(node.source, 'foo')
        self.assertEqual(node.COLOR, 'CYAN')

    def testFileNode(self):
        source = os.path.join(ROOT_DIR, 'docs', 'content', 'utilities', 'MooseDocs', 'index.md')
        node = page.FileNode(source=source)
        self.assertEqual(node.source, source)

class TestFindall(unittest.TestCase):
    """
    Tests for the LocationNodeBase.findall method.
    """
    def testBasic(self):
        root = page.DirectoryNode(source='docs')
        index = page.FileNode(root, source='docs/index.md')
        core = page.FileNode(root, source='docs/core.md')
        sub = page.DirectoryNode(root, source='docs/sub')
        core2 = page.FileNode(sub, source='docs/sub/core.md')
        full = page.FileNode(sub, source='docs/sub/full_core.md')

        nodes = root.findall('core.md')
        self.assertEqual(len(nodes), 3)
        self.assertIs(nodes[0], core)
        self.assertIs(nodes[1], core2)
        self.assertIs(nodes[2], full)

        nodes = root.findall('/core.md')
        self.assertEqual(len(nodes), 2)
        self.assertIs(nodes[0], core)
        self.assertIs(nodes[1], core2)

        nodes = root.findall('docs/core.md')
        self.assertEqual(len(nodes), 1)
        self.assertIs(nodes[0], core)

    def testErrors(self):
        root = page.DirectoryNode(source='docs')
        index = page.FileNode(root, source='docs/index.md')
        core = page.FileNode(root, source='docs/core.md')
        sub = page.DirectoryNode(root, source='docs/sub')
        core2 = page.FileNode(root, source='docs/sub/core.md')

        with self.assertRaises(TypeError) as e:
            root.findall('foo', maxcount=2.2)
        self.assertIn("The 'maxcount' input must be an integer", str(e.exception))

        with self.assertRaises(ValueError) as e:
            nodes = root.findall('core.md', maxcount=1)
        self.assertIn("The 'maxcount' was set to 1 but 2", str(e.exception))




if __name__ == '__main__':
    unittest.main(verbosity=2)
