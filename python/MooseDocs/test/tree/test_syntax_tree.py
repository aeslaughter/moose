#!/usr/bin/env python
import os
import unittest
import mock

import MooseDocs
from MooseDocs.common import exceptions
from MooseDocs.tree import app_syntax


class TestSyntaxTree(unittest.TestCase):


    def testRemoveDisable(self):
        location = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
        root = app_syntax(location, remove=[])
        node = root.findfull('/Variables/InitialCondition/BoundingBoxIC')
        self.assertEqual(node.name, 'BoundingBoxIC')


    def testRemove(self):
        location = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
        root = app_syntax(location)

        node = root.findfull('/Variables/InitialCondition/AddICAction')
        self.assertEqual(node.name, 'AddICAction')

        node = root.findfull('/Variables/InitialCondition/BoundingBoxIC')
        self.assertIsNone(node)

    def testRemoveTestApp(self):
        location = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
        root = app_syntax(location, None)
        self.assertNotIn('MiscTest', root.groups)

        location = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
        root = app_syntax(location, remove_test_apps=False)
        self.assertIn('MiscTest', root.groups)


if __name__ == '__main__':
    unittest.main(verbosity=2)
