#!/usr/bin/env python3
import os
import unittest
import factory

class TestMooseObject(unittest.TestCase):
    def testInit(self):
        loc = os.path.join(os.path.dirname(__file__), 'src', 'TestObject.py')
        f = factory.Factory(loc)
        self.assertEqual(len(f._Factory__objects), 2)
        self.assertEqual(list(f._Factory__objects.keys()), ['TestObject', 'TestObject2'])

        loc = os.path.join(os.path.dirname(__file__), 'src')
        f = factory.Factory(loc)
        self.assertEqual(len(f._Factory__objects), 2)
        self.assertEqual(list(f._Factory__objects.keys()), ['TestObject', 'TestObject2'])

        with self.assertRaises(OSError) as e:
            f = factory.Factory('wrong', 'nope.py')
        self.assertIn('The following paths', str(e.exception))
        self.assertIn('wrong', str(e.exception))
        self.assertIn('nope.py', str(e.exception))
        self.assertTrue(False)

    def testCreate(self):
        loc = os.path.join(os.path.dirname(__file__), 'src', 'TestObject.py')
        f = factory.Factory(loc)
        obj = f.create('TestObject', name='test')
        self.assertEqual(obj.name(), 'test')

        obj = f.create('TestObject2', name='test2')
        self.assertEqual(obj.name(), 'test2')

        with self.assertRaises(OSError) as e:
            f.create("wrong")
        self.assertIn('TestObject', str(e.exception))
        self.assertIn('TestObject2', str(e.exception))

if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2, buffer=True)
