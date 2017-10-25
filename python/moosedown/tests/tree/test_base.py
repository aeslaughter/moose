#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown.tree import base

class TestProperty(unittest.TestCase):
    """
    Tests for base.Property() class.
    """
    def testBasic(self):
        prop = base.Property('foo')
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.value, None)
        self.assertEqual(prop.type, None)
        self.assertEqual(prop.required, False)

    def testDefault(self):
        prop = base.Property('foo', 42)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.value, 42)
        self.assertEqual(prop.type, None)
        self.assertEqual(prop.required, False)

    def testType(self):
        prop = base.Property('foo', 42, int)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.value, 42)
        self.assertEqual(prop.type, int)
        self.assertEqual(prop.required, False)

    def testRequired(self):
        prop = base.Property('foo', 42, int, True)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.value, 42)
        self.assertEqual(prop.type, int)
        self.assertEqual(prop.required, True)

    def testKeyword(self):
        prop = base.Property('foo', required=True, default=42, ptype=int)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.value, 42)
        self.assertEqual(prop.type, int)
        self.assertEqual(prop.required, True)

    def testValueSetter(self):
        prop = base.Property('foo', required=True, default=42, ptype=int)
        prop.value = 43
        self.assertEqual(prop.value, 43)

        with self.assertRaises(TypeError) as e:
            prop.value = 'string'
        self.assertIn("must be of type 'int'", e.exception.message)

    def testConstructTypeError(self):
        with self.assertRaises(TypeError) as e:
            base.Property('foo', 42, str)
        self.assertIn("must be of type 'str'", e.exception.message)

class TestNodeBase(unittest.TestCase):
    """
    Tests for NodeBase class.
    """

    def testRoot(self):
        node = base.NodeBase(None)
        self.assertEqual(node.parent, None)

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
            PROPERTIES = [base.Property('month'), base.Property('day'), base.Property('year')]

        items = dict(month='june', day=24, year=1980)
        node = Date(**items)
        self.assertEqual(node.attributes, items)

        node.month = 'august'
        self.assertEqual(node.month, 'august')

    @mock.patch('logging.Logger.error')
    def testAttributeError(self, mock):
        node = base.NodeBase(None)
        #node.year
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

        @base.properties(base.Property('bar'), base.Property('bar2', 1980), base.Property('one', 1, int))
        class Foo(base.NodeBase):
            pass
            #bar = base.Property()
            #bar2 = base.Property(1980)
            #one = base.Property(1, int)

        foo = Foo()
        self.assertTrue(hasattr(foo, 'bar'))
        foo.bar = 42
        self.assertEqual(foo.bar, 42)

        self.assertEqual(foo.bar2, 1980)
        foo.bar2 = 1981
        self.assertEqual(foo.bar2, 1981)

        self.assertEqual(foo.one, 1)
        with self.assertRaises(TypeError) as e:
            foo.one = 1.1
        self.assertIn("must be of type 'int'", e.exception.message)

        with self.assertRaises(TypeError) as e:
            @base.properties(base.Property('bar', 1, str))
            class Foo2(base.NodeBase):
                pass
        self.assertIn("must be of type 'str'", e.exception.message)

if __name__ == '__main__':
    unittest.main(verbosity=2)
