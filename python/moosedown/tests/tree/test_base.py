#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown.tree import base

class TestProperty(unittest.TestCase):

    def testBasic(self):
        prop = base.Property('foo')
        self.assertEqual(prop.key, 'foo')
        self.assertEqual(prop.default, None)
        self.assertEqual(prop.type, None)

    def testDefault(self):
        prop = base.Property('foo', 42)
        self.assertEqual(prop.key, 'foo')
        self.assertEqual(prop.default, 42)
        self.assertEqual(prop.type, None)

    def testType(self):
        prop = base.Property('foo', 42, int)
        self.assertEqual(prop.key, 'foo')
        self.assertEqual(prop.default, 42)
        self.assertEqual(prop.type, int)

    def testConstructTypeError(self):
        with self.assertRaises(TypeError) as e:
            base.Property('foo', 42, str)
        self.assertIn("must be of type 'str'", e.exception.message)

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
        class Date(base.NodeBase):
            month = base.Property('month')
            day = base.Property('day')
            year = base.Property('year')

        items = dict(month='june', day=24, year=1980)
        node = Date(**items)
        self.assertEqual(node.attributes, items)

        node.month = 'august'
        self.assertNotEqual(node.attributes, items)
        self.assertEqual(node.month, 'august')

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

    def testContains(self):
        node = base.NodeBase(None, name='test', key='value', foo=None)
        self.assertIn('key', node)
        self.assertNotIn('foo', node)

        class TestNode(base.NodeBase):
            REQUIRED_ATTRIBUTES = ['foo']
        with self.assertRaises(ValueError) as e:
            node = TestNode(None, name='test', key='value')
        self.assertIn("The key 'foo'", e.exception.message)

    def testName(self):
        node = base.NodeBase(None, name='test')
        self.assertEqual(node.name, 'test')

        node = base.NodeBase(None)
        self.assertEqual(node.name, 'NodeBase')

    def testProperties(self):

        class Foo(base.NodeBase):
            PROPERTIES = [base.Property('bar'),
                          base.Property('bar2', 1980),
                          base.Property('one', 1, int)]

        foo = Foo()
        self.assertTrue(hasattr(foo, 'bar'))
        foo.bar = 42
        self.assertEqual(foo.bar, 42)

        self.assertEqual(foo.bar2, 1980)
        foo.bar2 = 1981
        x = foo.bar2
        self.assertEqual(foo.bar2, 1981)

        self.assertEqual(foo.one, 1)
        with self.assertRaises(TypeError) as e:
            foo.one = 1.1
        self.assertIn("'one' must be of type 'int'", e.exception.message)

        with self.assertRaises(TypeError) as e:
            class Foo2(base.NodeBase):
                PROPERTIES = [base.Property('bar', 1, str)]
        self.assertIn("'bar' must be of type 'str'", e.exception.message)



if __name__ == '__main__':
    unittest.main(verbosity=2)
