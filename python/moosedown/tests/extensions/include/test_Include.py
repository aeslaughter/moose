#!/usr/bin/env python
import os
import unittest
import logging
import mock
import glob
import tempfile

from moosedown import ROOT_DIR
from moosedown.tree import page, tokens
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestIncludeTokenize(testing.MarkdownTestCase):
    def setUp(self):
        testing.MarkdownTestCase.setUp(self)

        loc = tempfile.mkdtemp()
        self.files = [os.path.join(loc, 'file0.md'),
                      os.path.join(loc, 'file1.md'),
                      os.path.join(loc, 'file2.md')]

        with open(self.files[0], 'w') as fid:
            fid.write('File 0\n\n!include {}'.format(os.path.basename(self.files[1])))
        with open(self.files[1], 'w') as fid:
            fid.write('File 1\n\n!include {}'.format(os.path.basename(self.files[2])))
        with open(self.files[2], 'w') as fid:
            fid.write('File 2')

        self.root = page.DirectoryNode(None, source=loc)
        page.MarkdownNode(self.root, base=os.path.dirname(loc), source=self.files[0])
        page.MarkdownNode(self.root, base=os.path.dirname(loc), source=self.files[1])
        page.MarkdownNode(self.root, base=os.path.dirname(loc), source=self.files[2])
        for child in self.root:
            child.read()

    def tearDown(self):
        for fname in self.files:
            if os.path.exists(fname):
                os.remove(fname)

    def testAST(self):
        ast, _ = self.root(0).build(self._translator)
        for i in range(3):
            self.assertIsInstance(ast(i), tokens.Paragraph)
            self.assertIsInstance(ast(i)(0), tokens.Word)
            self.assertIsInstance(ast(i)(1), tokens.Space)
            self.assertIsInstance(ast(i)(2), tokens.Number)
            self.assertEqual(ast(i)(0).content, u'File')
            self.assertEqual(ast(i)(2).content, unicode(i))

    def testMaster(self):
        ast, _ = self.root(0).build(self._translator)
        self.assertEqual(self.root(0).master, set())
        self.assertEqual(self.root(1).master, set([self.root(0)]))
        self.assertEqual(self.root(2).master, set([self.root(1)]))

    def testMasterBuild(self):
        """
        ast, _ = self.root(0).build(self._translator)
        with open(self.files[0], 'w') as fid:
            fid.write('File 1 updated\n\n!include {}'.format(os.path.basename(self.files[1])))
        ast, _ = self.root(0).build(self._translator)
        self.assertIsInstance(ast(0)(4), tokens.Word)
        self.assertEqual(ast(0)(4).content, u'updated')


        with open(self.files[1], 'w') as fid:
            fid.write('File 2 updated\n\n!include {}'.format(os.path.basename(self.files[2])))
        ast, _ = self.root(0).build(self._translator)
        self.assertIsInstance(ast(0)(4), tokens.Word)
        self.assertEqual(ast(0)(4).content, u'updated')
        self.assertIsInstance(ast(1)(4), tokens.Word)
        self.assertEqual(ast(1)(4).content, u'updated')

        with open(self.files[2], 'w') as fid:
            fid.write('File 3 updated')
        ast, _ = self.root(0).build(self._translator)
        self.assertIsInstance(ast(0)(4), tokens.Word)
        self.assertEqual(ast(0)(4).content, u'updated')
        self.assertIsInstance(ast(1)(4), tokens.Word)
        self.assertEqual(ast(1)(4).content, u'updated')
        self.assertIsInstance(ast(2)(4), tokens.Word)
        self.assertEqual(ast(2)(4).content, u'updated')
        """

if __name__ == '__main__':
    unittest.main(verbosity=2)
