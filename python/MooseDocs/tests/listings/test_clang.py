#!/usr/bin/env python
import os
import unittest
import MooseDocs
from MooseDocs.testing import MarkdownTestCase

class TestMooseMooseCppMethod(MarkdownTestCase):
    """
    Test commands in MooseCppMethod
    """
    EXTENSIONS = ['MooseDocs.extensions.listings']

    def testClang(self):
        md = '!listing framework/src/kernels/Diffusion.C method=computeQpResidual'
        self.assertConvert('testClang.html', md)

    def testClangDeclaration(self):
        md = '!listing framework/src/kernels/Diffusion.C method=computeQpResidual declaration=1'
        self.assertConvert('testClangDeclaration.html', md)

    def testClangMethodError(self):
        md = '!listing framework/src/kernels/Diffusion.C method=not_a_valid_function'
        self.assertConvert('testClangMethodError.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
