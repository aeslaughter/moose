#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown.tree import base


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

    def testName(self):
        node = base.NodeBase(None, name='test')
        self.assertEqual(node.name, 'test')

        node = base.NodeBase(None)
        self.assertEqual(node.name, 'NodeBase')

class TestProperty(unittest.TestCase):
    """
    Tests for base.Property() class.
    """
    def testBasic(self):
        prop = base.Property('foo')
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.default, None)
        self.assertEqual(prop.type, None)
        self.assertEqual(prop.required, False)

    def testDefault(self):
        prop = base.Property('foo', 42)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.default, 42)
        self.assertEqual(prop.type, None)
        self.assertEqual(prop.required, False)

    def testType(self):
        prop = base.Property('foo', 42, int)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.default, 42)
        self.assertEqual(prop.type, int)
        self.assertEqual(prop.required, False)

    def testRequired(self):
        prop = base.Property('foo', 42, int, True)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.default, 42)
        self.assertEqual(prop.type, int)
        self.assertEqual(prop.required, True)

    def testKeyword(self):
        prop = base.Property('foo', required=True, default=42, ptype=int)
        self.assertEqual(prop.name, 'foo')
        self.assertEqual(prop.default, 42)
        self.assertEqual(prop.type, int)
        self.assertEqual(prop.required, True)

    def testConstructTypeError(self):
        with self.assertRaises(TypeError) as e:
            base.Property('foo', 42, str)
        self.assertIn("must be of type 'str'", e.exception.message)

class TestNodeBaseWithProperties(unittest.TestCase):
    """
    Tests for NodeBase class with @properties decorator.
    """

    def testProperties(self):

        @base.properties(base.Property('month'), base.Property('year', 1980),
                         base.Property('day', 24, int))
        class Date(base.NodeBase):
            pass

        # Construction and defaults
        node = Date()
        self.assertTrue(hasattr(node, 'year'))
        self.assertEqual(node.year, 1980)
        self.assertTrue(hasattr(node, 'month'))
        self.assertEqual(node.month, None)
        self.assertTrue(hasattr(node, 'day'))
        self.assertEqual(node.day, 24)

        # Change properties
        node.day = 27
        self.assertEqual(node.day, 27)
        node.year = 1949
        self.assertEqual(node.year, 1949)
        node.month = 'august' # change type allowed because it was not set on construction
        self.assertEqual(node.month, 'august')

        # Set error
        with self.assertRaises(TypeError) as e:
            node.day = 1.1
        self.assertIn("must be of type 'int'", e.exception.message)

    def testPropertiesWithKwargs(self):
        @base.properties(base.Property('hour', ptype=int), base.Property('minute'))
        class Time(base.NodeBase):
            pass

        t = Time(hour=6)
        self.assertEqual(t.hour, 6)

        with self.assertRaises(TypeError) as e:
            Time(hour='str')
        self.assertIn("must be of type 'int'", e.exception.message)

    def testPropertiesRequired(self):
        @base.properties(base.Property('hour', required=True))
        class Time(base.NodeBase):
            pass

        with self.assertRaises(TypeError) as e:
            Time()
        self.assertIn("The property 'hour' must be defined.", e.exception.message)

if __name__ == '__main__':
    unittest.main(verbosity=2)
