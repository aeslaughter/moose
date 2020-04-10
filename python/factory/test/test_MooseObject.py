#!/usr/bin/env python
#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import sys
import re
import unittest
from factory import MooseObject
from parameters import InputParameters

class TestMooseObject(unittest.TestCase):

    def testInit(self):
        obj = MooseObject()
        self.assertIn('name', obj.parameters())

        obj = MooseObject(name='Andrew')
        self.assertIn('name', obj.parameters())
        self.assertEqual(obj.getParam('name'), 'Andrew')

        obj = MooseObject(InputParameters())
        self.assertNotIn('name', obj.parameters())

        obj = MooseObject(InputParameters(), MooseObject.validParams())
        self.assertIn('name', obj.parameters())

        obj = MooseObject(InputParameters(), MooseObject.validParams(), name='Andrew')
        self.assertIn('name', obj.parameters())
        self.assertEqual(obj.getParam('name'), 'Andrew')

    def testErrorMode(self):

        obj = MooseObject(InputParameters(InputParameters.ErrorMode.ERROR))
        with self.assertLogs(level='ERROR') as log:
            obj.getParam('name')
        self.assertEqual(len(log.output), 1)
        self.assertIn("Cannot get value, the parameter 'name' does not exist.", log.output[0])

        obj = MooseObject(error_mode=InputParameters.ErrorMode.ERROR)
        with self.assertLogs(level='ERROR') as log:
            obj.getParam('wrong')
        self.assertEqual(len(log.output), 1)
        self.assertIn("Cannot get value, the parameter 'wrong' does not exist.", log.output[0])

        with self.assertLogs(level='WARNING') as log:
            obj = MooseObject(InputParameters(), error_mode=InputParameters.ErrorMode.ERROR)
        self.assertEqual(len(log.output), 1)
        self.assertIn("The following parameters do not exist: error_mode", log.output[0])

    def testName(self):
        obj = MooseObject()
        self.assertIsNone(obj.getParam('name'))
        self.assertEqual(obj.name(), 'MooseObject')

        obj = MooseObject(name='Andrew')
        self.assertEqual(obj.getParam('name'), 'Andrew')
        self.assertEqual(obj.name(), 'Andrew')

        obj = MooseObject(InputParameters())
        with self.assertLogs(level='WARNING') as log:
            obj.getParam('name')
        self.assertEqual(len(log.output), 1)
        self.assertIn("Cannot get value, the parameter 'name' does not exist.", log.output[0])

        with self.assertLogs(level='WARNING') as log:
            obj = MooseObject(InputParameters(), name='Andrew')
        self.assertEqual(len(log.output), 1)
        self.assertIn("The following parameters do not exist: name", log.output[0])

    def testGetParam(self):
        obj = MooseObject()
        self.assertIsNone(obj.getParam('name'))

        with self.assertLogs(level='WARNING') as log:
            obj.getParam('wrong')
        self.assertEqual(len(log.output), 1)
        self.assertIn("Cannot get value, the parameter 'wrong' does not exist.", log.output[0])

    def testIsParamValid(self):
        obj = MooseObject()
        self.assertFalse(obj.isParamValid('name'))

        obj = MooseObject(name='Andrew')
        self.assertTrue(obj.isParamValid('name'))

        with self.assertLogs(level='WARNING') as log:
            obj.isParamValid('wrong')
        self.assertEqual(len(log.output), 1)
        self.assertIn("Cannot determine if the parameters is valid, the parameter 'wrong' does not exist.", log.output[0])

    def testLogger(self):
        obj = MooseObject()
        with self.assertLogs(level='INFO') as log:
            obj.info("foo")
        self.assertEqual(len(log.output), 1)
        self.assertIn("foo", log.output[0])

        with self.assertLogs(level='WARNING') as log:
            obj.warning("foo")
        self.assertEqual(len(log.output), 1)
        self.assertIn("foo", log.output[0])

        with self.assertLogs(level='ERROR') as log:
            obj.error("foo")
        self.assertEqual(len(log.output), 1)
        self.assertIn("foo", log.output[0])

        with self.assertLogs(level='DEBUG') as log:
            obj.debug("foo")
        self.assertEqual(len(log.output), 1)
        self.assertIn("foo", log.output[0])

if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2, buffer=True, exit=False)
