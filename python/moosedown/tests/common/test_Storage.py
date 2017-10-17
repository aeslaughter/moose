#!/usr/bin/env python
import unittest
from MooseDocs import common

class TestStorage(unittest.TestCase):
    """
    Test the Storage object.
    """
    def testAdd(self):
        """
        Use add an __iter__ access
        """
        storage = common.Storage(int)
        storage.add('one', 1)
        storage.add('four', 4)
        storage.add('three', 3)
        self.assertEqual(list(storage), [1,4,3])

        with self.assertRaises(TypeError) as cm:
            storage.add('value', 1.2)
        self.assertIn('Incorrect object provided, expected', str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            storage.add('one', 11)
        self.assertIn("The key 'one' already", str(cm.exception))

    def testGetItem(self):
        """
        Test operator[] access
        """
        storage = common.Storage(int)
        storage.add('one', 1)
        storage.add('four', 4)
        storage.add('three', 3)

        # str access
        self.assertEqual(storage['four'], 4)
        self.assertEqual(storage['one'], 1)
        self.assertEqual(storage['three'], 3)

        # int access
        self.assertEqual(storage[0], 1)
        self.assertEqual(storage[1], 4)
        self.assertEqual(storage[2], 3)

        # wrong type
        with self.assertRaises(TypeError) as cm:
            storage[1.2]
        self.assertIn("The supplied type must be 'int'", str(cm.exception))

        # bad index
        with self.assertRaises(IndexError):
            storage[42]

        # bad key
        with self.assertRaises(ValueError):
            storage['42']

    def testContains(self):
        """
        Test 'in' operator.
        """
        storage = common.Storage(int)
        storage.add('one', 1)
        storage.add('four', 4)
        storage.add('three', 3)

        # str
        self.assertIn('one', storage)
        self.assertIn('four', storage)
        self.assertIn('three', storage)

        # int
        self.assertIn(0, storage)
        self.assertIn(1, storage)
        self.assertIn(2, storage)

        # wrong type
        with self.assertRaises(TypeError) as cm:
            1.2 in storage
        self.assertIn("The supplied type must be 'int'", str(cm.exception))

        # not in
        self.assertNotIn('five', storage)
        self.assertNotIn(42, storage)

    def testInsert(self):
        """
        Test that the insert methods work.
        """
        storage = common.Storage(int)
        storage.add('one', 1)
        storage.add('four', 4)

        storage.add('two', 2, '>one')
        self.assertEqual(storage[1], 2)

        storage.add('three', 3, '<four')
        self.assertEqual(storage[2], 3)

        storage.add('five', 5, '_end')
        self.assertEqual(storage[4], 5)

        storage.add('zero', 0, '_begin')
        self.assertEqual(storage[0], 0)

        storage.add('negative', -1, 0)
        self.assertEqual(storage[0], -1)

        storage.add('answer', 42, len(storage))
        self.assertEqual(storage[-1], 42)


if __name__ == '__main__':
    unittest.main(verbosity=2)
