#!/usr/bin/env python
import unittest
import logging
import mock

from MooseDocs import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestExampleTokenize(testing.MooseDocsTestCase):
    def testBasic(self):
        pass
        #ex = self.ast('!devel example\n~~~\nfoo\n~~~\nbar')
        #print ex

    def testCaption(self):
        pass
        #ex = self.ast('!devel example caption=foo\n~~~\nfoo\n~~~\nbar')
        #print ex

if __name__ == '__main__':
    unittest.main(verbosity=2)
