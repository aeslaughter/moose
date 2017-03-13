#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestVideo(MarkdownTestCase):
    """
    Test the !video syntax
    """

    def testDefault(self):
        md = '!video http://clips.vorwaerts-gmbh.de/VfE.webm'
        self.assertConvert('test_Default.html', md)

    def testSettings(self):
        md = '!video http://clips.vorwaerts-gmbh.de/VfE.webm width=100% center=False autoplay=True'
        self.assertConvert('test_Settings.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
