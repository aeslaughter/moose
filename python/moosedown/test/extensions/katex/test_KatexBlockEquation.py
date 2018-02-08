#!/usr/bin/env python
import unittest
import moosedown
from moosedown.extensions import katex
from moosedown.base import testing

class TestLatexBlockEquationTokenize(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.katex]
    def testBasic(self):
        ast = self.ast(u'\\begin{equation}\nfoo\n\\end{equation}')
        self.assertIsInstance(ast(0), katex.LatexBlockEquation)

class TestLatexInlineEquationTokenize(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.katex]
    def testBasic(self):
        ast = self.ast(u'$foo$')
        self.assertIsInstance(ast(0)(0), katex.LatexInlineEquation)

if __name__ == '__main__':
    unittest.main(verbosity=2)
