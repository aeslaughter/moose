#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase
from MooseDocs.extensions.media import MediaPatternBase

class TestImage(MarkdownTestCase):
    """
    Test commands in MooseTextFile extension.
    """
    EXTENSIONS = ['MooseDocs.extensions.media']

    def setUp(self):
        """
        Clear counter before each run.
        """
        super(TestImage, self).setUp()
        MediaPatternBase.COUNTER.clear()

    def testDefault(self):
        md = '!media docs/media/github-logo.png'
        self.assertConvert('testDefault.html', md)

    def testDisableCount(self):
        md = '!media docs/media/github-logo.png counter=None\n\n'
        md += '!media docs/media/github-logo.png'
        self.assertConvert('testDisableCount.html', md)

    def testCount(self):
        md = '!media docs/media/github-logo.png\n\n'
        md += '!media docs/media/inl_blue.png'
        self.assertConvert('testCount.html', md)

    def testChangeCounter(self):
        md = '!media docs/media/github-logo.png\n\n'
        md += '!media docs/media/inl_blue.png counter=foo\n\n'
        md += '!media docs/media/github-logo.png\n\n'
        self.assertConvert('testChangeCounter.html', md)

    def testDisableMaterializeBox(self):
        md = '!media docs/media/github-logo.png materialboxed=false counter=None'
        self.assertConvert('testDisableMaterializeBox.html', md)

    def testCaption(self):
        md = '!media docs/media/github-logo.png caption=A test caption counter=None'
        self.assertConvert('testCaption.html', md)

    def testSettings(self):
        md = '!media docs/media/github-logo.png float=right width=30% counter=None'
        self.assertConvert('testSettings.html', md)

    def testCard(self):
        md = '!media docs/media/github-logo.png card=true'
        self.assertConvert('testCard.html', md)

    def testCardCaption(self):
        md = '!media docs/media/github-logo.png card=1 caption=A test caption counter=None'
        self.assertConvert('testCardCaption.html', md)

    def testFileError(self):
        md = '!media docs/media/not_a_file.png'
        self.assertConvert('testFileError.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
