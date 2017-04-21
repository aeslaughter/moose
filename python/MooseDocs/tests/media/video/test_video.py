#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestVideo(MarkdownTestCase):
    """
    Test the !media syntax for video files.
    """
    EXTENSIONS = ['MooseDocs.extensions.media']

    def testDefault(self):
        md = '!media http://clips.vorwaerts-gmbh.de/VfE.webm'
        self.assertConvert('testDefault.html', md)

    def testSettings(self):
        md = '!media http://clips.vorwaerts-gmbh.de/VfE.webm video-width=100% autoplay=True'
        self.assertConvert('testSettings.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
