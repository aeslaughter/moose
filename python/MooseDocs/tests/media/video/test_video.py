#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase
from MooseDocs.extensions.media import MediaPatternBase

class TestVideo(MarkdownTestCase):
    """
    Test the !media syntax for video files.
    """
    EXTENSIONS = ['MooseDocs.extensions.media']

    def setUp(self):
        """
        Clear counter before each run.
        """
        super(TestVideo, self).setUp()
        MediaPatternBase.COUNTER.clear()

    def testDefault(self):
        md = '!media http://clips.vorwaerts-gmbh.de/VfE.webm counter=None'
        self.assertConvert('testDefault.html', md)

    def testSettings(self):
        md = '!media http://clips.vorwaerts-gmbh.de/VfE.webm video-width=100% autoplay=True counter=None'
        self.assertConvert('testSettings.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
