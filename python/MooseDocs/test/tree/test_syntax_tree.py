#!/usr/bin/env python
import os
import unittest
import mock

import MooseDocs
from MooseDocs.common import exceptions
from MooseDocs.tree import app_syntax


class TestDocTree(unittest.TestCase):


    def testBasic(self):
        location = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
        root = app_syntax(location)
        node = root.findfull('/Variables/InitialCondition/BoundingBoxIC')
        self.assertEqual(node.name, 'BoundingBoxIC')


    def testExclude(self):
        location = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
        exclude = ['/Variables/InitialCondition/*',
                   '!/Variables/InitialCondition/AddICAction']
        root = app_syntax(location, exclude)

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
