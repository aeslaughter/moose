#!/usr/bin/env python3
"""
Test for request for Information.
"""
import os
import unittest
import logging
import vtk
import chigger2 as chigger

logging.basicConfig()

class TestChiggerAlgorithm(chigger.base.ChiggerAlgorithm):
    """Test class with dummy output for testing callback of ChiggerAlgorithm"""

    @staticmethod
    def validParams():
        params = chigger.base.ChiggerAlgorithm.validParams()
        params.add('test', 1)
        return params

    def __init__(self, **kwargs):
        super().__init__(nOutputPorts=1, outputType="vtkPolyData", **kwargs)
        self._vtksource = vtk.vtkCubeSource()
        self.n_mod = 0
        self.n_info = 0
        self.n_data = 0

    def _onRequestModified(self):
        super()._onRequestModified()
        self.n_mod += 1

    def _onRequestInformation(self, inInfo, outInfo):
        super()._onRequestInformation(inInfo, outInfo)
        self.n_info += 1

    def _onRequestData(self, inInfo, outInfo):
        super()._onRequestData(inInfo, outInfo)
        self.n_data += 1
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        self._vtksource.Update()
        opt.ShallowCopy(self._vtksource.GetOutput())

class TestInfoAlgorithm(unittest.TestCase):
    """
    A test case to ensure that file modified time changes are detected.
    """
    def testObjectInit(self):
        obj = TestChiggerAlgorithm()
        self.assertEqual(obj.n_mod, 0)

    def testObjectModified(self):
        obj = TestChiggerAlgorithm()
        t0 = obj.GetMTime()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.objectModified()
        self.assertNotEqual(t0, obj.GetMTime())
        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:objectModified', l.output[0])

    def testUpdateObject(self):
        obj = TestChiggerAlgorithm()
        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 0)
        self.assertEqual(obj.n_data, 0)

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateObject()

        self.assertEqual(len(l.output), 9)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateObject', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[4])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[5])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[6])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestData', l.output[7])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestData', l.output[8])

        self.assertEqual(obj.n_mod, 1)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 1)

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateObject()
        self.assertEqual(len(l.output), 5)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateObject', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[4])

        self.assertEqual(obj.n_mod, 2)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 1)

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.setParams(test=1) # Don't actually modify it
            obj.updateObject()

        self.assertEqual(len(l.output), 6)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:setParams', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateObject', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[4])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[5])

        self.assertEqual(obj.n_mod, 3)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 1)

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.setParams(test=2) # change it
            obj.updateObject()

        self.assertEqual(len(l.output), 11)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:setParams', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:objectModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateObject', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[4])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[5])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[6])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[7])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[8])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestData', l.output[9])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestData', l.output[10])

        self.assertEqual(obj.n_mod, 4)
        self.assertEqual(obj.n_info, 2)
        self.assertEqual(obj.n_data, 2)

    def testUpdateModified(self):
        obj = TestChiggerAlgorithm()
        t0 = obj.GetMTime()

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateModified()

        self.assertEqual(obj.GetMTime(), t0)
        self.assertEqual(len(l.output), 2)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[1])

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.parameters().update(test=2) # don't used setParams because that calls updateModified
            obj.updateModified()

        self.assertNotEqual(obj.GetMTime(), t0)

        self.assertEqual(len(l.output), 3)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:objectModified', l.output[2])

    def testUpdateInformation(self):
        obj = TestChiggerAlgorithm()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateInformation()

        self.assertEqual(len(l.output), 3)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[2])

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateInformation()

        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[0])

        obj.setParams(test=2)
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateInformation()

        self.assertEqual(len(l.output), 3)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[2])




if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
