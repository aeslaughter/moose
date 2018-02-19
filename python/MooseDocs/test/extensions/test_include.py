#!/usr/bin/env python
"""Testing for MooseDocs.extensions.include MooseDocs extension."""
import os
import unittest
import tempfile
import shutil

import anytree

import MooseDocs
from MooseDocs.extensions import core, include, command
from MooseDocs.tree import tokens, html, latex, page
from MooseDocs.base import testing, renderers

class TestIncludeBase(testing.MooseDocsTestCase):

    EXTENSIONS = [core, command, include]
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

# TOKEN OBJECTS TESTS
class TestTokens(TestIncludeBase):
    """Test Token object for MooseDocs.extensions.include MooseDocs extension."""

    def testIncludeToken(self):
        token = include.IncludeToken(include=self.root(0))
        self.assertIs(token.include, self.root(0))

# TOKENIZE TESTS
class TestIncludeTokenize(TestIncludeBase):
    """Test tokenization of Include"""

    def testToken(self):
        self.build()
        for i in range(4):
            ast = self.root(i).ast()
            self.assertIsInstance(ast(0), tokens.Paragraph)
            self.assertIsInstance(ast(0)(0), tokens.Word)
            self.assertIsInstance(ast(0)(1), tokens.Space)
            self.assertIsInstance(ast(0)(2), tokens.Number)
            self.assertEqual(ast(0)(0).content, u'File')
            self.assertEqual(ast(0)(2).content, unicode(i))

        # File0
        self.assertIsInstance(self.root(0).ast()(1), include.IncludeToken)
        self.assertIs(self.root(0).ast()(1).include, self.root(1))

        # File1
        self.assertIsInstance(self.root(1).ast()(1), include.IncludeToken)
        self.assertIs(self.root(1).ast()(1).include, self.root(2))

        # File2 (no includes)
        self.assertEqual(len(self.root(2).ast()), 1)

        # File3
        self.assertIsInstance(self.root(3).ast()(1), include.IncludeToken)
        self.assertIs(self.root(3).ast()(1).include, self.root(2))

    def testMaster(self):
        self.build()
        self.assertEqual(self.root(0).master, set())
        self.assertEqual(self.root(1).master, set([self.root(0)]))
        self.assertEqual(self.root(2).master, set([self.root(1), self.root(3)]))
        self.assertEqual(self.root(3).master, set())


# RENDERER TESTS
class TestRenderIncludeHTML(TestIncludeBase):
    """Test renderering of RenderInclude with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    def node(self):
        return self.root(0).render().find('moose-content', attr='class')

    def testTree(self):
        node = self.node()
        for i in range(3):
            self.assertIsInstance(node(i), html.Tag)
            self.assertIsInstance(node(i)(0), html.String)
            self.assertEqual(node(i)(0).content, u'File')

            self.assertIsInstance(node(i)(1), html.String)
            self.assertEqual(node(i)(1).content, u' ')

            self.assertIsInstance(node(i)(2), html.String)
            self.assertEqual(node(i)(2).content, unicode(i))


    def testWrite(self):
        node = self.node()
        for i in range(3):
            self.assertEqual(node(i).write(), u'<p>File {}</p>'.format(i))

class TestRenderIncludeMaterialize(TestRenderIncludeHTML):
    """Test renderering of RenderInclude with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

class TestRenderIncludeLatex(TestIncludeBase):
    """Test renderering of RenderInclude with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    def node(self):
        return self.root(0).render().find('document')

    def testTree(self):
        node = self.node()
        for i in range(0, 3, 4):
            self.assertIsInstance(node(i), latex.Command)
            self.assertIsInstance(node(i+1), latex.String)
            self.assertEqual(node(i+1).content, u'File')

            self.assertIsInstance(node(i+2), latex.String)
            self.assertEqual(node(i+2).content, u' ')

            self.assertIsInstance(node(i+3), latex.String)
            self.assertEqual(node(i+3).content, unicode(i))

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), u'\n\\begin{document}\n\n\\par\nFile 0\n\\par\nFile 1\n\\par\nFile 2\n\\end{document}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
