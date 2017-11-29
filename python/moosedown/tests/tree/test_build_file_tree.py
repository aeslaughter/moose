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

from moosedown import ROOT_DIR
from moosedown.tree.build_file_tree import build_regex
from moosedown.tree.build_file_tree import find_files
from moosedown.tree.build_file_tree import doc_import

class TestBuildRegex(unittest.TestCase):
    """
    Tests regex building test function.
    """
    def testBasic(self):
        path = '/one/**/four/five'
        self.assertEqual(build_regex(path), r'^/one/(?:.*?)/four/five$')

        path = '/one/two/three/four/**'
        self.assertEqual(build_regex(path), r'^/one/two/three/four/(?:.*?)$')

        path = '**/three/four/five'
        self.assertEqual(build_regex(path), r'^(?:.*?)/three/four/five$')

        path = '**/three/**'
        self.assertEqual(build_regex(path), r'^(?:.*?)/three/(?:.*?)$')

        path = '**/three/**/nine/**'
        self.assertEqual(build_regex(path), r'^(?:.*?)/three/(?:.*?)/nine/(?:.*?)$')

        path = '/one/*/four/five'
        self.assertEqual(build_regex(path), r'^/one/(?:[^/]*?)/four/five$')

        path = '/one/two/three/four/*'
        self.assertEqual(build_regex(path), r'^/one/two/three/four/(?:[^/]*?)$')

        path = '*/three/four/five'
        self.assertEqual(build_regex(path), r'^(?:[^/]*?)/three/four/five$')

        path = '*/three/*'
        self.assertEqual(build_regex(path), r'^(?:[^/]*?)/three/(?:[^/]*?)$')

        path = '*/three/*/nine/*'
        self.assertEqual(build_regex(path), r'^(?:[^/]*?)/three/(?:[^/]*?)/nine/(?:[^/]*?)$')

        path = '*/three/**/nine/*'
        self.assertEqual(build_regex(path), r'^(?:[^/]*?)/three/(?:.*?)/nine/(?:[^/]*?)$')

        path = '**/three/*/nine/**'
        self.assertEqual(build_regex(path), r'^(?:.*?)/three/(?:[^/]*?)/nine/(?:.*?)$')

        path = '**/three/*/nine/**/foo.md'
        self.assertEqual(build_regex(path), r'^(?:.*?)/three/(?:[^/]*?)/nine/(?:.*?)/foo\.md$')


class TestFindFiles(unittest.TestCase):
    """
    Test the file find function.
    """
    def testBasic(self):
        filenames = ['/one/two/three/four/a.md',
                     '/one/two/three/four/b.md',
                     '/one/two/three/four/c.md',
                     '/one/two/three/four/d.md',
                     '/one/two/not-three/four/a.md',
                     '/one/two/not-three/four/b.md',
                     '/one/two/three/four/five/a.md',
                     '/one/two/three/four/five/b.md',
                     '/one/two/three/four/five/c.md',
                     '/one/two/three/four/five/d.md']

        pattern = '/one/two/three/four/*'
        files = find_files(filenames, pattern)
        self.assertEqual(len(files), 4)
        self.assertEqual(files, set(filenames[:4]))

        pattern = '/one/two/three/four/**'
        files = find_files(filenames, pattern)
        self.assertEqual(len(files), 8)
        self.assertEqual(files, set(filenames[:4] + filenames[6:]))

        pattern = '/one/two/*/four/*'
        files = find_files(filenames, pattern)
        self.assertEqual(len(files), 6)
        self.assertEqual(files, set(filenames[:6]))

        pattern = '/one/**/four/*'
        files = find_files(filenames, pattern)
        self.assertEqual(len(files), 6)
        self.assertEqual(files, set(filenames[:6]))

        pattern = '**/four/*'
        files = find_files(filenames, pattern)
        self.assertEqual(len(files), 6)
        self.assertEqual(files, set(filenames[:6]))

        pattern = '**/five/*'
        files = find_files(filenames, pattern)
        self.assertEqual(len(files), 4)
        self.assertEqual(files, set(filenames[6:]))

class TestMooseDocsImport(unittest.TestCase):
    """
    Tests for docs_import function.
    """
    def testBasic(self):
        items = doc_import(content=['framework/doc/content/**',
                                    '!framework/doc/content/documentation/**'],
                           root_dir=ROOT_DIR,
                           extensions=('.md'))
        self.assertIsInstance(items, list)
        gold = '{}/framework/doc/content/utilities/moose_docs/moose_markdown/index.md'
        self.assertIn(gold.format(ROOT_DIR), items)

        gold = '{}/framework/doc/content/documentation/systems/Kernels/framework/Diffusion.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        self.assertTrue(all(x.endswith('.md') for x in items))

    def testFilename(self):
        items = doc_import(content=['framework/doc/content/utilities/moose_docs/*',
                                    'framework/doc/content/getting_started/*',
                                    '!framework/doc/content/utilities/memory_logger/*',
                                    '!framework/doc/**/moose_markdown/*'],
                            root_dir=ROOT_DIR,
                            extensions=('.md'))

        self.assertIsInstance(items, list)
        gold = '{}/framework/doc/content/utilities/moose_docs/moose_markdown/index.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        gold = '{}/framework/doc/content/documentation/systems/Kernels/framework/Diffusion.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        gold = '{}/framework/doc/content/utilities/memory_logger/memory_logger.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        gold = '{}/framework/doc/content/getting_started/create_an_app.md'
        self.assertIn(gold.format(ROOT_DIR), items)

        gold = '{}/framework/doc/content/utilities/moose_docs/moose_markdown/index.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

"""
    def testErrors(self):
        moose_docs_import(include=42)
        self.assertInLogError('The "include" must be a list of str items.')

        moose_docs_import(include=[42])
        self.assertInLogError('The "include" must be a list of str items.')

        moose_docs_import(exclude=42)
        self.assertInLogError('The "exclude" must be a list of str items.')

        moose_docs_import(exclude=[42])
        self.assertInLogError('The "exclude" must be a list of str items.')

    def testIndex(self):
        items = moose_docs_import(include=['docs/content/index.md'],
                                  base='docs/content',
                                  extensions=('.md'))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], os.path.join(MooseDocs.ROOT_DIR, 'docs', 'content', 'index.md'))

    def testExclude(self):
        items = moose_docs_import(include=['docs/content/**'],
                                  exclude=['docs/content/documentation/**/level_set/**'],
                                  base='docs/content',
                                  extensions=('.md'))

        gold = os.path.join(MooseDocs.ROOT_DIR,
                            'docs/content/documentation/systems/Kernels/framework/Diffusion.md')
        self.assertIn(gold, items)

        gold = os.path.join(MooseDocs.ROOT_DIR,
                            'docs/content/documentation/systems/Kernels/level_set/' \
                            'LevelSetAdvection.md')
        self.assertNotIn(gold, items)
"""

#TODO: error check that doc_import with invalid root_dir errors

if __name__ == '__main__':
    unittest.main(verbosity=2)
