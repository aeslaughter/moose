#!/usr/bin/env python
import unittest
import logging
import mock

from MooseDocs.tree import base

class TestNodeBase(unittest.TestCase):

    def testRoot(self):
        node = base.NodeBase(None)
        self.assertEqual(node.parent, None)
        self.assertEqual(node.attributes, dict())

    def testTree(self):
        root = base.NodeBase(None)
        node = base.NodeBase(root)
        self.assertIs(node.parent, root)
        self.assertIs(root.children[0], node)
        self.assertIs(root(0), node)

    @mock.patch('logging.Logger.error')
    def testCallError(self, mock):
        node = base.NodeBase(None)
        node(0)
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn('A child node with index', args[0])

    def testAttributes(self):
        items = dict(month='june', day=24, year=1980)
        node = base.NodeBase(None, **items)
        self.assertEqual(node.attributes, items)

        node['month'] = 'august'
        self.assertNotEqual(node.attributes, items)
        self.assertEqual(node['month'], 'august')

        items['month'] = 'august'
        self.assertEqual(node.attributes, items)

    @mock.patch('logging.Logger.error')
    def testAttributeError(self, mock):
        node = base.NodeBase(None)
        node['year']
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn('Unknown attribute', args[0])

    def testWrite(self):
        node = base.NodeBase(None)
        with self.assertRaises(NotImplementedError) as e:
            node.write()
        self.assertIn("The write() method is not", e.exception.message)

    def testIter(self):
        root = base.NodeBase(None)
        child0 = base.NodeBase(root)
        child1 = base.NodeBase(root)
        self.assertEqual(list(root), [child0, child1])

if __name__ == '__main__':
    unittest.main(verbosity=2)
