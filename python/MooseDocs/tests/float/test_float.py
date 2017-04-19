#!/usr/bin/env python
import os
import unittest
from MooseDocs.testing import MarkdownTestCase

class TestFloat(MarkdownTestCase):
    """
    Test commands in MooseTextFile extension.
    """

    def testTextListing(self):
        md = '!text framework/src/kernels/Diffusion.C id=diffusion caption=Diffusion Kernel'
        self.assertConvert('test_TextListing.html', md)

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

if __name__ == '__main__':
    unittest.main(verbosity=2)
