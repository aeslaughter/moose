#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestListings(MarkdownTestCase):
    """
    Test the linstings extension
    """
    EXTENSIONS = ['MooseDocs.extensions.listings', 'MooseDocs.extensions.refs']

    def testDefault(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i'
        self.assertConvert('testDefault.html', md)

    def testStart(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=[Outputs]'
        self.assertConvert('testStart.html', md)

    def testEnd(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i end=[Variables]'
        self.assertConvert('testEnd.html', md)

    def testStartEnd(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=[Variables] end=[BCs]'
        self.assertConvert('testStartEnd.html', md)

    def testStartEndIncludeEnd(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=[Variables] end=[BCs] include_end=True'
        self.assertConvert('testStartEndIncludeEnd.html', md)

    def testLine(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i line=ernel'
        self.assertConvert('testLine.html', md)

    def testContentError(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i line=notfound'
        self.assertConvert('testContentError.html', md)

    def testFileError(self):
        md = '!listing test/tests/kernels/simple_diffusion/not_a_file.'
        self.assertConvert('testFileError.html', md)

    def testCaption(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=[Outputs] caption=Outputs Block'
        self.assertConvert('testCaption.html', md)

    def testCaptionId(self):
        md = '!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=[Outputs] id=foo caption=Outputs Block'
        self.assertConvert('testCaptionId.html', md)

    """
    def testInputListing(self):
        md = '!input test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels id=diffusion_block caption=Diffusion Kernel Input Syntax'
        self.assertConvert('test_InputListing.html', md)

    def testClangListing(self):
        md = '!clang framework/src/kernels/Diffusion.C method=computeQpResidual id=diffusion_compute caption=Diffusion Kernel computeQpResidual'
        self.assertConvert('test_ClangListing.html', md)

    def testMultipleListing(self):
        md = '!text framework/src/kernels/Diffusion.C id=diffusion caption=Diffusion Kernel\n\n'
        md += '!input test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels id=diffusion_block caption=Diffusion Kernel Input Syntax\n\n'
        md += 'Listing \\ref{diffusion} and \\ref{diffusion_block}.'
        self.assertConvert('test_MultipleListing.html', md)

    def testImageFigure(self):
        md = '!image docs/media/github-logo.png id=github_logo caption=GitHub Logo\n\n'
        md += 'This is a reference to Figure \\ref{github_logo}.'
        self.assertConvert('test_ImageFigure.html', md)

    def testVideoFigure(self):
        md = '!video http://clips.vorwaerts-gmbh.de/VfE.webm id=big_buck caption=Big Buck Bunny\n\n'
        md += 'This is a reference to Figure \\ref{big_buck}.'
        self.assertConvert('test_VideoFigure.html', md)
    """

if __name__ == '__main__':
    unittest.main(verbosity=2)
