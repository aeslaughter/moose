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


    @unittest.skip('')
    def testImageCaption(self):
        md = '!image docs/media/github-logo.png caption=A test caption'
        self.assertConvert('testImageCaption.html', md)

    @unittest.skip('')
    def testImageSettings(self):
        md = '!image docs/media/github-logo.png float=right width=30%'
        self.assertConvert('test_ImageSettings.html', md)

    @unittest.skip('')
    def testImageBadFile(self):
        md = '!image docs/media/not_a_file.png'
        self.assertConvert('test_ImageBadFile.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
