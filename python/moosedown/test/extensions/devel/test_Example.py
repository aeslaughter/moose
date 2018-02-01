#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestExampleTokenize(testing.MooseDocsTestCase):
    """Example tokenize"""

    def testBasic(self):
        ex = self.ast('!devel example\n~~~\nfoo\n~~~\nbar')
        #print ex


    def testCaption(self):
        ex = self.ast('!devel example caption=foo\n~~~\nfoo\n~~~\nbar')
        #print ex



if __name__ == '__main__':
    unittest.main(verbosity=2)
