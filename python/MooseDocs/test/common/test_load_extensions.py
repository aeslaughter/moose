#!/usr/bin/env python
import unittest
import mock

import MooseDocs
from MooseDocs import common
from MooseDocs.common import exceptions
from MooseDocs import base

class TestLoadExtensions(unittest.TestCase):
    def testLoadFromModule(self):
        ext = common.load_extensions([MooseDocs.extensions.core])
        self.assertIsInstance(ext, list)
        self.assertIsInstance(ext[0], MooseDocs.extensions.core.CoreExtension)

    def testLoadFromModuleWithConfig(self):
        ext = common.load_extensions([MooseDocs.extensions.devel],
                                     {'MooseDocs.extensions.devel':{'preview':False}})
        self.assertFalse(ext[0]['preview'])

    def testLoadFromStr(self):
        ext = common.load_extensions(['MooseDocs.extensions.core'])
        self.assertIsInstance(ext, list)
        self.assertIsInstance(ext[0], MooseDocs.extensions.core.CoreExtension)

    def testLoadFromStrWithConfig(self):
        ext = common.load_extensions(['MooseDocs.extensions.devel'],
                                     {'MooseDocs.extensions.devel':{'preview':False}})
        self.assertFalse(ext[0]['preview'])

    def testMissingMakeExtension(self):
        with self.assertRaises(exceptions.MooseDocsException) as e:
            ext = common.load_extensions([MooseDocs.extensions])
        self.assertIn("does not contain the required 'make_extension'", e.exception.message)

    def testBadModuleName(self):
        with self.assertRaises(exceptions.MooseDocsException) as e:
            ext = common.load_extensions(['not.a.module'])
        self.assertIn("Failed to import the supplied", e.exception.message)

    def testBadModuleType(self):
        with self.assertRaises(exceptions.MooseDocsException) as e:
            ext = common.load_extensions([42])
        self.assertIn("must be a module type", e.exception.message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
