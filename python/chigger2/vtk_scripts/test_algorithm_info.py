#!/usr/bin/env python3
"""
Test for request for Information.
"""
import unittest
import os
import shutil
import time
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class InfoAlgorithm(VTKPythonAlgorithmBase):
    def __init__(self, filename):
        VTKPythonAlgorithmBase.__init__(self)
        self.SetNumberOfInputPorts(0)
        self.SetNumberOfOutputPorts(0)

        self._filename = filename
        self._filename_m_time = None

    def FileModifiedTime(self):
        return self._filename_m_time

    def RequestInformation(self, request, inInfo, outInfo):
        self._filename_m_time = os.path.getmtime(self._filename)
        return 1

class TestInfoAlgorithm(unittest.TestCase):
    """
    A test case to ensure that file modified time changes are detected.
    """
    TEST_FILENAME = 'algorithm_info.txt'

    def setUp(self):
        """Create base file for testing."""
        with open(self.TEST_FILENAME, 'w') as fid:
            fid.write("This is a test.")

    def tearDown(self):
        """Destroy temporary files."""
        if os.path.exists(self.TEST_FILENAME):
            os.remove(self.TEST_FILENAME)

    def updateFileModifiedTime(self, sleep=0.1):
        """Helper to change modified time of the test file."""
        time.sleep(sleep)
        os.utime(self.TEST_FILENAME)

    def getFileModifiedTime(self):
        """Helper for returning the modified time of the test file."""
        return os.path.getmtime(self.TEST_FILENAME)

    def testModifiedTime(self):
        """Make certain the helper function is working."""
        t0 = self.getFileModifiedTime()
        self.updateFileModifiedTime()
        t1 = self.getFileModifiedTime()
        self.assertTrue(t1 > t0)

    def testAlgorithm(self):
        """Test the InfoAlgorithm class."""

        info = InfoAlgorithm(self.TEST_FILENAME)
        info.UpdateInformation()

        t0 = info.FileModifiedTime()
        self.assertEqual(t0, self.getFileModifiedTime())
        self.updateFileModifiedTime()

        # This call to UpdateInformation does not call RequestInformation, what I am doing wrong?
        info.GetInformation().Modified() # This seems like it should work
        info.UpdateInformation()
        t1 = info.FileModifiedTime()

        self.assertTrue(self.getFileModifiedTime() > t0) # Tests that the file modified is changed

        self.assertTrue(t1 > t0)  # This fails because RequestInformation isn't being called

if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
