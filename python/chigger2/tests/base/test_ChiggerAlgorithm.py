#!/usr/bin/env python3
"""
Test for request for Information.
"""
import unittest
import os
import shutil
import time
import vtk
import chigger2 as chigger

class TestChiggerAlgorithm(chigger.base.ChiggerAlgorithm):
    """Test class with dummy output for testing callback of ChiggerAlgorithm"""
    def __init__(self):
        ChiggerAlgorithm.__init__(nOutputPorts=1, outputType="vtkPolyData")
        self._vtksource = vtk.vtkCubeSource()
        self.request_mod_count = 0
        self.request_info_count = 0
        self.request_data_count = 0

    def _onRequestModified(self):
        ChiggerAlgorithm._onRequestModified(self)
        self.request_mod_count += 1

    def _onRequestInformation(self, inInfo, outInfo):
        ChiggerAlgorithm._onRequestInformation(self, inInfo, outInfo)
        self.request_info_count += 1

    def _onRequestData(self, inInfo, outInfo):
        ChiggerAlgorithm._onRequestData(self, inInfo, outInfo)
        self._request_data_count += 1
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        self._vtksource.Update()
        opt.ShallowCopy(self._vtksource.GetOutput())

class TestInfoAlgorithm(unittest.TestCase):
    """
    A test case to ensure that file modified time changes are detected.
    """




    def testRequestInformation(self):
        """Test the InfoAlgorithm class."""

        info = InfoAlgorithm(self.TEST_FILENAME)
        info.UpdateInformation()
        self.assertEqual(info.GetRequestInformationCount(), 1)

        # This call to UpdateInformation does not call RequestInformation, what I am doing wrong?
        #info.GetInformation().Modified() # This seems like it should work
        info.Modified()
        info.UpdateInformation()
        self.assertEqual(info.GetRequestInformationCount(), 2)


    def testRequestData(self):
        """Test the InfoAlgorithm class."""
        info = InfoAlgorithm(self.TEST_FILENAME)
        info.UpdateInformation()
        info.Update()

        self.assertEqual(info.GetRequestDataCount(), 1)

        info.Modified()
        info.UpdateInformation()
        info.Update()

        self.assertEqual(info.GetRequestDataCount(), 2)


if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
