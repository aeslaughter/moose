#!/usr/bin/env python
#pylint: disable=missing-docstring
####################################################################################################
#                                    DO NOT MODIFY THIS HEADER                                     #
#                   MOOSE - Multiphysics Object Oriented Simulation Environment                    #
#                                                                                                  #
#                              (c) 2010 Battelle Energy Alliance, LLC                              #
#                                       ALL RIGHTS RESERVED                                        #
#                                                                                                  #
#                            Prepared by Battelle Energy Alliance, LLC                             #
#                               Under Contract No. DE-AC07-05ID14517                               #
#                               With the U. S. Department of Energy                                #
#                                                                                                  #
#                               See COPYRIGHT for full restrictions                                #
####################################################################################################
import os
import unittest
import StringIO
import MooseDocs
from MooseDocs.testing import LogTestCase
from MooseDocs.common import moose_docs_import

class TestMooseDocsImport(LogTestCase):
    """
    Tests for MooseDocsImport object.
    """
    def testBasic(self):
        items = moose_docs_import(include=['docs/content/*'],
                                  exclude=['docs/content/documentation/*'],
                                  root=MooseDocs.ROOT_DIR,
                                  extension='.md')

        self.assertIsInstance(items, list)
        gold = '{}/docs/content/utilities/moose_docs/moose_markdown/index.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertIn(gold, items)

        gold = '{}/docs/content/documentation/systems/Kernels/framework/Diffusion.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertNotIn(gold, items)

        self.assertTrue(all(x.endswith('.md') for x in items))

    def testFilename(self):
        items = moose_docs_import(include=['docs/content/utilities/moose_docs/*'],
                                  exclude=['docs/content/utilities/memory_logger/*'],
                                  filename='python/MooseDocs/tests/common/import/test_import',
                                  root=MooseDocs.ROOT_DIR,
                                  extension='.md')

        self.assertIsInstance(items, list)
        gold = '{}/docs/content/utilities/moose_docs/moose_markdown/index.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertNotIn(gold, items)

        gold = '{}/docs/content/documentation/systems/Kernels/framework/Diffusion.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertNotIn(gold, items)

        gold = '{}/docs/content/documentation/utilities/memory_logger/memory_logger.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertNotIn(gold, items)

        gold = '{}/docs/content/getting_started/create_an_app.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertIn(gold, items)

        gold = '{}/docs/content/utilities/moose_docs/moose_markdown/index.md'. \
               format(MooseDocs.ROOT_DIR)
        self.assertNotIn(gold, items)

    def testErrors(self):
        moose_docs_import(include=42)
        self.assertInLogError('The "include" must be a list of str items.')

        moose_docs_import(include=[42])
        self.assertInLogError('The "include" must be a list of str items.')

        moose_docs_import(exclude=42)
        self.assertInLogError('The "exclude" must be a list of str items.')

        moose_docs_import(exclude=[42])
        self.assertInLogError('The "exclude" must be a list of str items.')

        filename =  'not/a/real/file.txt'
        moose_docs_import(filename=filename)
        self.assertInLogError('The file {} does not exists.'.format(os.path.abspath(filename)))



if __name__ == '__main__':
    unittest.main(verbosity=2)
