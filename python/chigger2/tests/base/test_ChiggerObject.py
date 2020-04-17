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

class TestChiggerObject(chigger.base.ChiggerObject):
    """Test class with dummy output for testing callback of ChiggerAlgorithm"""

    @staticmethod
    def validParams():
        params = chigger.base.ChiggerObject.validParams()
        params.add('test', 1)
        return params

class ChiggerObjectTestCase(unittest.TestCase):
    def testObjectInit(self):
        obj = TestChiggerObject()
        self.assertEqual(obj.getParam('test'), 1)

    def testSetParam(self):
        obj = TestChiggerObject()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.setParam('test', 2)
        self.assertEqual(obj.getParam('test'), 2)
        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerObject:setParam', l.output[0])

    def testSetParams(self):
        obj = TestChiggerObject()
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.setParams(test=2)
        self.assertEqual(obj.getParam('test'), 2)
        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerObject:setParams', l.output[0])

    def testAssignParam(self):
        class Test(object):
            def __init__(self):
                self.value = 0
            def func(self, v):
                self.value = v

        t = Test()
        obj = TestChiggerObject()
        self.assertEqual(t.value, 0)
        with self.assertLogs(level=logging.DEBUG) as l:
            obj.assignParam('test', t.func)
        self.assertEqual(t.value, 1)
        self.assertEqual(len(l.output), 1)
        self.assertEqual('DEBUG:TestChiggerObject:assignParam', l.output[0])

if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
