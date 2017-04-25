#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestImage(MarkdownTestCase):
    """
    Test commands in MooseTextFile extension.
    """
    EXTENSIONS = ['MooseDocs.extensions.media']

    def testDefault(self):
        md = '!media docs/media/github-logo.png'
        self.assertConvert('testDefault.html', md)

    def testDefaultId(self):
        md = '!media docs/media/github-logo.png id=github'
        self.assertConvert('testDefaultId.html', md)

    def testDisableCount(self):
        md = '!media docs/media/github-logo.png\n\n'
        md += '!media docs/media/github-logo.png id=github'
        self.assertConvert('testDisableCount.html', md)

    def testCount(self):
        md = '!media docs/media/github-logo.png id=github1\n\n'
        md += '!media docs/media/inl_blue.png id=github2'
        self.assertConvert('testCount.html', md)

    def testChangeCounter(self):
        md = '!media docs/media/github-logo.png id=fig1\n\n'
        md += '!media docs/media/inl_blue.png counter=foo id=foo1\n\n'
        md += '!media docs/media/github-logo.png id=fig2\n\n'
        self.assertConvert('testChangeCounter.html', md)

    def testDisableMaterializeBox(self):
        md = '!media docs/media/github-logo.png materialboxed=false'
        self.assertConvert('testDisableMaterializeBox.html', md)

    def testCaption(self):
        md = '!media docs/media/github-logo.png caption=A test caption'
        self.assertConvert('testCaption.html', md)

    def testSettings(self):
        md = '!media docs/media/github-logo.png float=right width=30%'
        self.assertConvert('testSettings.html', md)

    def testCard(self):
        md = '!media docs/media/github-logo.png card=true'
        self.assertConvert('testCard.html', md)

    def testCardCaption(self):
        md = '!media docs/media/github-logo.png card=1 caption=A test caption'
        self.assertConvert('testCardCaption.html', md)

    def testFileError(self):
        md = '!media docs/media/not_a_file.png'
        self.assertConvert('testFileError.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
