#!/usr/bin/env python
import os
import unittest
import logging
import mock
import glob
import tempfile
import time
import shutil

import anytree

import moosedown
from moosedown import ROOT_DIR
from moosedown.tree import page, tokens
from moosedown.extensions import include
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestIncludeTokenize(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.command, moosedown.extensions.include]
    def setUp(self):
        testing.MooseDocsTestCase.setUp(self)

        self.loc = tempfile.mkdtemp()
        self.files = [os.path.join(self.loc, 'file0.md'),
                      os.path.join(self.loc, 'file1.md'),
                      os.path.join(self.loc, 'file2.md'),
                      os.path.join(self.loc, 'file3.md')]

        with open(self.files[0], 'w') as fid:
            fid.write('File 0\n\n!include {}'.format(os.path.basename(self.files[1])))
        with open(self.files[1], 'w') as fid:
            fid.write('File 1\n\n!include {}'.format(os.path.basename(self.files[2])))
        with open(self.files[2], 'w') as fid:
            fid.write('File 2')
        with open(self.files[3], 'w') as fid:
            fid.write('File 3\n\n!include {}'.format(os.path.basename(self.files[2])))

        self.root = page.DirectoryNode(None, source=self.loc)
        page.MarkdownNode(self.root, base=os.path.dirname(self.loc), source=self.files[0])
        page.MarkdownNode(self.root, base=os.path.dirname(self.loc), source=self.files[1])
        page.MarkdownNode(self.root, base=os.path.dirname(self.loc), source=self.files[2])
        page.MarkdownNode(self.root, base=os.path.dirname(self.loc), source=self.files[3])

        for node in anytree.PreOrderIter(self.root):
            node.init(self._translator)

    def build(self):
        for child in self.root:
            child.build()

    def tearDown(self):
        shutil.rmtree(self.loc)

    def testAST(self):
        self.build()
        for i in range(4):
            ast = self.root(i).ast
            self.assertIsInstance(ast(0), tokens.Paragraph)
            self.assertIsInstance(ast(0)(0), tokens.Word)
            self.assertIsInstance(ast(0)(1), tokens.Space)
            self.assertIsInstance(ast(0)(2), tokens.Number)
            self.assertEqual(ast(0)(0).content, u'File')
            self.assertEqual(ast(0)(2).content, unicode(i))

        # File0
        self.assertIsInstance(self.root(0).ast(1), include.IncludeToken)
        self.assertIs(self.root(0).ast(1).include, self.root(1))

        # File1
        self.assertIsInstance(self.root(1).ast(1), include.IncludeToken)
        self.assertIs(self.root(1).ast(1).include, self.root(2))

        # File2 (no includes)
        self.assertEqual(len(self.root(2).ast), 1)

        # File3
        self.assertIsInstance(self.root(3).ast(1), include.IncludeToken)
        self.assertIs(self.root(3).ast(1).include, self.root(2))

    def testMaster(self):
        self.build()
        self.assertEqual(self.root(0).master, set())
        self.assertEqual(self.root(1).master, set([self.root(0)]))
        self.assertEqual(self.root(2).master, set([self.root(1), self.root(3)]))
        self.assertEqual(self.root(3).master, set())

if __name__ == '__main__':
    unittest.main(verbosity=2)
