#!/usr/bin/env python
import unittest
import moosedown
from moosedown.extensions import katex
from moosedown.base import testing

class TestKatexInlineEquationComponentTokenize(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.katex]
    def testBasic(self):
        ast = self.ast(u'$foo$')
        self.assertIsInstance(ast(0)(0), katex.LatexInlineEquation)

if __name__ == '__main__':
    unittest.main(verbosity=2)
