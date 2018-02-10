#!/usr/bin/env python
import os
import unittest
import mooseutils

class TestHitLoad(unittest.TestCase):
    """
    Test the hit_load function.
    """

    def testRender(self):
        root = mooseutils.hit_load(os.path.join('..', '..', 'test_files', 'test.hit'))
        out = root.render()
        self.assertIn('[A]', out)
        self.assertIn('param = bar', out)
        self.assertIn('comment', out)

    def testBasic(self):
        root = mooseutils.hit_load(os.path.join('..', '..', 'test_files', 'test.hit'))
        self.assertEqual(root.children[0].name, 'A')
        self.assertEqual(root.children[0]['param'], 'foo')
        self.assertEqual(root.children[0].children[0].name, 'A-1')
        self.assertIn('param', root.children[0].children[0])
        self.assertEqual(root.children[0].children[0]['param'], 'bar')

        self.assertEqual(root.children[1].name, 'B')
        self.assertEqual(root.children[1].children[0].name, 'B-1')
        self.assertEqual(root.children[1].children[0].children[0].name, 'B-1-1')
        self.assertIn('type', root.children[1].children[0].children[0])
        self.assertEqual(root.children[1].children[0].children[0]['type'], 'test')
        self.assertEqual(root.children[1].children[1].name, 'B-2')

        gold = ['A', 'B']
        for i, child in enumerate(root):
            self.assertEqual(child.name, gold[i])

    def testFind(self):
        root = mooseutils.hit_load(os.path.join('..', '..', 'test_files', 'test.hit'))
        self.assertIs(root.find('A'), root.children[0])
        self.assertEqual(root.findall('A'), [root.children[0], root.children[0].children[0]])
        self.assertEqual(root.findall('-1'),
                         [root.children[0].children[0],
                          root.children[1].children[0],
                          root.children[1].children[0].children[0]])

        self.assertEqual(root.children[1].findall('-1'),
                         [root.children[1].children[0],
                          root.children[1].children[0].children[0]])

if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
