#!/usr/bin/env python
import unittest
import moosedown
from moosedown import tree
from moosedown.base import testing

class TestEndOfFileTokenize(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.katex]
    def testBasic(self):
        # TODO:As far as I can tell the core.EndOfFile component is not reachable, if a way to reach
        # it found then it needs to get added to this test.
        ast = self.ast(u'foo\n     ')(0)
        self.assertIsInstance(ast, tree.tokens.Paragraph)

if __name__ == '__main__':
    unittest.main(verbosity=2)
