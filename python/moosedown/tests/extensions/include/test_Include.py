#!/usr/bin/env python
import os
import unittest
import logging
import mock
import glob

from moosedown import ROOT_DIR
from moosedown.tree import page
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestIncludeTokenize(testing.MarkdownTestCase):
    """Code tokenize"""

    def testBasic(self):
        base = os.path.join(ROOT_DIR, 'docs', 'content', 'utilities', 'moosedown')
        root = page.DirectoryNode(None, source=base)

        for filename in glob.glob(os.path.join(base, '*.md')):
            node = page.MarkdownNode(root, source=filename)
            node.read()

        idx = root.find('index.md')
        inc = root.find('include.md')

        ast = self._translator.ast(idx)
        print ast
        self.assertIs(inc.master, idx)

if __name__ == '__main__':
    unittest.main(verbosity=2)
