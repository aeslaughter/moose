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

class ChiggerAlgorithmTestCase(unittest.TestCase):
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

        self.assertEqual(obj.n_mod, 1)
        self.assertEqual(obj.n_info, 0)
        self.assertEqual(obj.n_data, 0)

        self.assertEqual(obj.GetMTime(), t0)
        self.assertEqual(len(l.output), 2)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[1])

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.parameters().update(test=2) # don't used setParams because that calls updateModified
            obj.updateModified()

        self.assertEqual(obj.n_mod, 2)
        self.assertEqual(obj.n_info, 0)
        self.assertEqual(obj.n_data, 0)

        self.assertNotEqual(obj.GetMTime(), t0)

        self.assertEqual(len(l.output), 3)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateModified', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:objectModified', l.output[2])

    def testUpdateInformation(self):
        obj = TestChiggerAlgorithm()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateInformation()

        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 0)

        self.assertEqual(len(l.output), 3)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[2])

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateInformation()

        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 0)

        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[0])

        obj.setParams(test=2)
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateInformation()

        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 2)
        self.assertEqual(obj.n_data, 0)

        self.assertEqual(len(l.output), 3)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateInformation', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[2])

    def testUpdateData(self):
        obj = TestChiggerAlgorithm()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateData()

        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 1)

        self.assertEqual(len(l.output), 5)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestData', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestData', l.output[4])

        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateData()

        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 1)
        self.assertEqual(obj.n_data, 1)

        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[0])

        obj.setParams(test=2)
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.updateData()

        self.assertEqual(obj.n_mod, 0)
        self.assertEqual(obj.n_info, 2)
        self.assertEqual(obj.n_data, 2)

        self.assertEqual(len(l.output), 5)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:updateData', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestInformation', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestInformation', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:RequestData', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:_onRequestData', l.output[4])

    def testSetParam(self):
        obj = TestChiggerAlgorithm()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.setParam('test', 2)

        self.assertEqual(len(l.output), 2)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:setParam', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:objectModified', l.output[1])

    def testSetParams(self):
        obj = TestChiggerAlgorithm()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.setParams(test=2)

        self.assertEqual(len(l.output), 2)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:setParams', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:objectModified', l.output[1])

    def testAddObject(self):
        parent = TestChiggerAlgorithm(name="parent")
        child = TestChiggerAlgorithm(name="child")
        parent._addAlgorithm(child)

        with self.assertLogs(level=logging.DEBUG) as l:
            parent.updateObject()

        self.assertEqual(len(l.output), 17)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateObject', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):updateModified', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):_onRequestModified', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):_onRequestModified', l.output[4])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateInformation', l.output[5])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):updateInformation', l.output[6])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):RequestInformation', l.output[7])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):_onRequestInformation', l.output[8])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):RequestInformation', l.output[9])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):_onRequestInformation', l.output[10])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateData', l.output[11])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):updateData', l.output[12])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):RequestData', l.output[13])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(child):_onRequestData', l.output[14])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):RequestData', l.output[15])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):_onRequestData', l.output[16])

        with self.assertLogs(level=logging.ERROR) as l:
            parent._addAlgorithm("Wrong")

        self.assertEqual(len(l.output), 1)
        self.assertIn("The supplied object must be a ChiggerAlgorithm type", l.output[0])

        del child
        with self.assertLogs(level=logging.DEBUG) as l:
            parent.updateObject()

        print('\n'.join(l.output))
        self.assertEqual(len(l.output), 5)
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateObject', l.output[0])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateModified', l.output[1])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):_onRequestModified', l.output[2])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateInformation', l.output[3])
        self.assertEqual('DEBUG:TestChiggerAlgorithm:(parent):updateData', l.output[4])



if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
