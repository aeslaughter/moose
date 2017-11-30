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
import mock

from moosedown import ROOT_DIR
from moosedown.tree.build_page_tree import build_regex
from moosedown.tree.build_page_tree import find_files
from moosedown.tree.build_page_tree import doc_import
from moosedown.tree.build_page_tree import doc_tree
from moosedown.tree import page

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

class TestDocImport(unittest.TestCase):
    """
    Tests for docs_import function.
    """
    def testBasic(self):
        items = doc_import(content=['framework/doc/content/**',
                                    '!framework/doc/content/documentation/**'],
                           root_dir=ROOT_DIR)
        self.assertIsInstance(items, list)

        gold = '{}/framework/doc/content/documentation/systems/Kernels/framework/Diffusion.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)


    def testFilename(self):
        items = doc_import(content=['docs/content/utilities/moose_docs/*',
                                    'docs/content/getting_started/*',
                                    '!docs/content/utilities/memory_logger/*',
                                    '!docs/**/moose_markdown/*'],
                            root_dir=ROOT_DIR)

        self.assertIsInstance(items, list)
        gold = '{}/docs/content/utilities/moose_docs/moose_markdown/index.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        gold = '{}/docs/content/documentation/systems/Kernels/framework/Diffusion.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        gold = '{}/docs/content/utilities/memory_logger/memory_logger.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

        gold = '{}/docs/content/getting_started/petsc_default.md'
        self.assertIn(gold.format(ROOT_DIR), items)

        gold = '{}/docs/content/utilities/moose_docs/moose_markdown/index.md'
        self.assertNotIn(gold.format(ROOT_DIR), items)

    @mock.patch('logging.Logger.error')
    def testErrors(self, mock):

        doc_import('', content=dict())
        args, _ = mock.call_args
        self.assertIn('The "content" must be a list of str items.', args[-1])

        doc_import('', content=[1])
        args, _ = mock.call_args
        self.assertIn('The "content" must be a list of str items.', args[-1])

        doc_import('not/valid', content=['foo'])
        args, _ = mock.call_args
        self.assertIn('The "root_dir" must be a valid directory', args[-1])

class TestDocTree(unittest.TestCase):
    """
    Test creation of file tree nodes.
    """
    def testBasic(self):

        items = [dict(root_dir=os.path.join(ROOT_DIR, 'docs/content'),
                      content=['getting_started/**']),
                 dict(root_dir=os.path.join(ROOT_DIR, 'framework/doc/content'),
                      content=['documentation/systems/Adaptivity/**'])]

        root = doc_tree(items)

        self.assertIsInstance(root(0), page.DirectoryNode)
        self.assertEqual(root(0).name, 'getting_started')
        self.assertEqual(root(0).source,
                         os.path.join(ROOT_DIR, 'docs/content/getting_started'))

        self.assertIsInstance(root(0)(0), page.DirectoryNode)
        self.assertEqual(root(0)(0).name, 'installation')
        self.assertEqual(root(0)(0).source,
                         os.path.join(ROOT_DIR, 'docs/content/getting_started/installation'))

        self.assertIsInstance(root(0)(0)(0), page.MarkdownNode)
        self.assertEqual(root(0)(0)(0).name, 'build_libmesh.md')
        self.assertEqual(root(0)(0)(0).source,
                         os.path.join(ROOT_DIR,
                                      'docs/content/getting_started/installation/build_libmesh.md'))



if __name__ == '__main__':
    unittest.main(verbosity=2)
