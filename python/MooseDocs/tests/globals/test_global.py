#!/usr/bin/env python
import os
import unittest
import MooseDocs
from MooseDocs.testing import MarkdownTestCase

class TestGlobalExtension(MarkdownTestCase):
    """
    Test commands in GlobalExtension
    """

    def testLink(self):
        self.assertConvert('test_Link.html', '[libMesh]')

if __name__ == '__main__':
    unittest.main(verbosity=2)
