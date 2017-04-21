#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestMooseImageFile(MarkdownTestCase):
    """
    Test commands in MooseTextFile extension.
    """
    EXTENSIONS = ['MooseDocs.extensions.media']

    def testImageDefault(self):
        md = '!media docs/media/github-logo.png'
        self.assertConvert('testImageDefault.html', md)

    def testImageDisableMaterializeBox(self):
        md = '!media docs/media/github-logo.png materialboxed=false'
        self.assertConvert('testImageDisableMaterializeBox.html', md)

    def testImageCaption(self):
        md = '!media docs/media/github-logo.png caption=A test caption'
        self.assertConvert('testImageCaption.html', md)

    def testImageSettings(self):
        md = '!media docs/media/github-logo.png float=right width=30%'
        self.assertConvert('testImageSettings.html', md)

    def testImageCard(self):
        md = '!media docs/media/github-logo.png card=true'
        self.assertConvert('testImageCard.html', md)

    def testImageCardCaption(self):
        md = '!media docs/media/github-logo.png card=1 caption=A test caption'
        self.assertConvert('testImageCardCaption.html', md)

    def testImageFileError(self):
        md = '!media docs/media/not_a_file.png'
        self.assertConvert('testImageFileError.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
