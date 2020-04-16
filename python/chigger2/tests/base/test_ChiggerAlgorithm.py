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
from vtk.util import keys

class InfoAlgorithm(VTKPythonAlgorithmBase):
    def __init__(self, filename):
        VTKPythonAlgorithmBase.__init__(self)
        self.SetNumberOfInputPorts(0)
        self.SetNumberOfOutputPorts(1)
        self.OutputType = 'vtkPolyData'


        self.ModifiedRequest = vtk.vtkInformation()

        key = keys.MakeKey(keys.RequestKey, "REQUEST_MODIFIED", self.__class__.__name__)
        key.Set(self.ModifiedRequest, 1)
        print(self.ModifiedRequest)
        #print(info)


        self._request_info_count = 0
        self._request_data_count = 0

        self._vtksource = vtk.vtkCubeSource()

    def updateInformation(self):



    def GetRequestInformationCount(self):
        return self._request_info_count

    def GetRequestDataCount(self):
        return self._request_data_count

    def RequestInformation(self, request, inInfo, outInfo):
        self._request_info_count += 1
        #print('\nRequestInformation:\n', outInfo.GetInformationObject(0))
        #print('\nRequestInformation:\n', self.GetExecutive())
        return 1

    def RequestData(self, request, inInfo, outInfo):
        print('REQUEST', request)
        self._request_data_count += 1
        #print('\nRequestData:\n', outInfo.GetInformationObject(0))
        #print('\nRequestData:\n', self.GetExecutive())

        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        self._vtksource.Update()
        opt.ShallowCopy(self._vtksource.GetOutput())
        return 1

class TestInfoAlgorithm(unittest.TestCase):
    """
    A test case to ensure that file modified time changes are detected.
    """
    TEST_FILENAME = 'algorithm_info.txt'

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
