#!/usr/bin/env python
import os
import unittest
import mooseutils

class TestYamlLoad(unittest.TestCase):
    """
    Test that the size function returns something.
    """
    def testLoad(self):
        data = mooseutils.yaml_load('bar.yml')
        self.assertEqual(data[0], 3.6)
        self.assertEqual(data[1], [1,2,3])
        self.assertEqual(data[2], 'item')
        self.assertEqual(data[3], 'other')

    def testInclude(self):
        data = mooseutils.yaml_load('foo.yml')
        self.assertEqual(data['a'], 1)
        self.assertEqual(data['b'], [1.43, 543.55])
        self.assertEqual(data['c'][0], 3.6)
        self.assertEqual(data['c'][1], [1,2,3])
        self.assertEqual(data['c'][2], 'item')
        self.assertEqual(data['c'][3], 'other')


if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2, buffer=True, exit=False)
