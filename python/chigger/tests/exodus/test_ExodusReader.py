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

import os
import unittest
import shutil
import time
import logging
import mooseutils
import chigger

class TestExodusReader(unittest.TestCase):
    """
    Test use of MooseDataFrame for loading/reloading csv files.
    """
    @classmethod
    def setUpClass(cls):
        """
        Copy test files.
        """
        cls.single = "{}_single.e".format(cls.__name__)
        shutil.copyfile(os.path.abspath('../input/mug_blocks_out.e'), cls.single)

        cls.vector = "{}_vector.e".format(cls.__name__)
        shutil.copyfile(os.path.abspath('../input/vector_out.e'), cls.vector)

        cls.multiple = "{}_multiple".format(cls.__name__)
        cls.testfiles = chigger.utils.copy_adaptive_exodus_test_files(cls.multiple)
        cls.multiple += '.e'

        cls.interpolate = "{}_interpolate.e".format(cls.__name__)
        shutil.copyfile(os.path.abspath('../input/input_no_adapt_out.e'), cls.interpolate)

        cls.duplicate = "{}_duplicate.e".format(cls.__name__)
        shutil.copyfile(os.path.abspath('../input/duplicate_name_out.e'), cls.duplicate)

    @classmethod
    def tearDownClass(cls):
        """
        Remove test files.
        """
        for fname in cls.testfiles:
            if os.path.exists(fname):
                os.remove(fname)
        if os.path.exists(cls.single):
            os.remove(cls.single)
        if os.path.exists(cls.vector):
            os.remove(cls.vector)
        if os.path.exists(cls.interpolate):
            os.remove(cls.interpolate)
        if os.path.exists(cls.duplicate):
            os.remove(cls.duplicate)

    def testSingle(self):
        """
        Test reading of a single Exodus file, with default options
        """
        reader = chigger.exodus.ExodusReader(self.single)

        # Times
        times = reader.getTimes()
        self.assertEqual(len(times), 21)
        self.assertEqual(times[0], 0)
        self.assertAlmostEqual(times[-1], 2)

        # Current Time
        reader.setOptions(timestep=None, time=1.01)
        tdata0, tdata1 = reader.getTimeInformation()
        self.assertAlmostEqual(tdata0.time, 1)
        self.assertEqual(tdata0.timestep, 10)
        self.assertEqual(tdata0.index, 10)
        self.assertEqual(tdata0.filename, self.single)

        self.assertAlmostEqual(tdata1.time, 1.1)
        self.assertEqual(tdata1.timestep, 11)
        self.assertEqual(tdata1.index, 11)
        self.assertEqual(tdata1.filename, self.single)

        # Blocks
        blockinfo = reader.getBlockInformation()
        self.assertEqual(sorted(list(blockinfo[reader.BLOCK].keys())), ['1', '76',])
        self.assertEqual(sorted(list(blockinfo[reader.NODESET].keys())), ['1', '2'])
        self.assertEqual(sorted(list(blockinfo[reader.SIDESET].keys())), ['1', '2'])
        self.assertEqual(blockinfo[reader.SIDESET]['2'].name, 'top')
        self.assertEqual(blockinfo[reader.SIDESET]['2'].object_type, 3)
        self.assertEqual(blockinfo[reader.SIDESET]['2'].object_index, 1)
        self.assertEqual(blockinfo[reader.SIDESET]['2'].multiblock_index, 9)

        # Variable Info
        varinfo = reader.getVariableInformation()
        self.assertEqual([v.name for v in varinfo], ['aux_elem', 'convected', 'diffused', 'func_pp'])

        # Elemental Variables
        elemental = reader.getVariableInformation(var_types=[reader.ELEMENTAL])
        self.assertEqual([v.name for v in elemental], ['aux_elem'])
        self.assertEqual(elemental[0].num_components, 1)

        # Nodal Variables
        nodal = reader.getVariableInformation(var_types=[reader.NODAL])
        self.assertEqual([v.name for v in nodal], ['convected', 'diffused'])
        self.assertEqual(nodal[1].num_components, 1)

        # Global Variables
        gvars = reader.getVariableInformation(var_types=[reader.GLOBAL])
        self.assertEqual([v.name for v in gvars], ['func_pp'])
        self.assertEqual(gvars[0].num_components, 1)

    def testSingleNoInterpolation(self):
        """
        Test reading of a single Exodus file, without time interpolation
        """
        reader = chigger.exodus.ExodusReader(self.single)

        # Times
        times = reader.getTimes()
        self.assertEqual(len(times), 21)
        self.assertEqual(times[0], 0)
        self.assertAlmostEqual(times[-1], 2)

        # Current Time
        reader.setOptions(timestep=None, time=1.01, time_interpolation=False)
        tdata0, tdata1 = reader.getTimeInformation()

        self.assertAlmostEqual(tdata0.time, 1)
        self.assertEqual(tdata0.timestep, 10)
        self.assertEqual(tdata0.index, 10)
        self.assertEqual(tdata0.filename, self.single)

        self.assertIsNone(tdata1)

    def testTimeInterpolation(self):
        reader = chigger.exodus.ExodusReader(self.interpolate)

        reader.UpdateInformation()
        reader.Update()
        data = reader.GetOutputDataObject(0).GetBlock(0).GetBlock(0)

        # Time = 10
        cdata = data.GetCellData()
        self.assertEqual(cdata.GetNumberOfArrays(), 2)
        self.assertEqual(cdata.GetNumberOfComponents(), 2)
        self.assertEqual(cdata.GetNumberOfTuples(), 1600)
        self.assertEqual(cdata.GetArray(0).GetName(), 'elemental')
        self.assertEqual(cdata.GetArray(1).GetName(), 'ObjectId')
        rng = cdata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -9.93844170297569)
        self.assertAlmostEqual(rng[1], 9.93844170297569)

        ndata = data.GetPointData()
        self.assertEqual(ndata.GetNumberOfArrays(), 1)
        self.assertEqual(ndata.GetNumberOfComponents(), 1)
        self.assertEqual(ndata.GetNumberOfTuples(), 1681)
        self.assertEqual(ndata.GetArray(0).GetName(), 'nodal')
        rng = ndata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -10)
        self.assertAlmostEqual(rng[1], 10)

        gdata = data.GetFieldData()
        self.assertEqual(gdata.GetNumberOfArrays(), 4)
        self.assertEqual(gdata.GetArray(0).GetName(), 'global')
        self.assertEqual(gdata.GetArray(0).GetComponent(2, 0), 10)

        # Time = 5
        reader.setOptions(time=5)
        reader.Update()
        data = reader.GetOutputDataObject(0).GetBlock(0).GetBlock(0)
        cdata = data.GetCellData()
        self.assertEqual(cdata.GetNumberOfArrays(), 2)
        self.assertEqual(cdata.GetNumberOfComponents(), 2)
        self.assertEqual(cdata.GetNumberOfTuples(), 1600)
        self.assertEqual(cdata.GetArray(0).GetName(), 'elemental')
        self.assertEqual(cdata.GetArray(1).GetName(), 'ObjectId')
        rng = cdata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -4.969220851487845)
        self.assertAlmostEqual(rng[1], 4.969220851487845)

        ndata = data.GetPointData()
        self.assertEqual(ndata.GetNumberOfArrays(), 1)
        self.assertEqual(ndata.GetNumberOfComponents(), 1)
        self.assertEqual(ndata.GetNumberOfTuples(), 1681)
        self.assertEqual(ndata.GetArray(0).GetName(), 'nodal')
        rng = ndata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -5)
        self.assertAlmostEqual(rng[1], 5)

        gdata = data.GetFieldData()
        self.assertEqual(gdata.GetNumberOfArrays(), 4)
        self.assertEqual(gdata.GetArray(0).GetName(), 'global')
        self.assertEqual(gdata.GetArray(0).GetComponent(1, 0), 5)

        # Time = 7.5
        reader.setOptions(time=7.5)
        reader.Update()
        data = reader.GetOutputDataObject(0).GetBlock(0).GetBlock(0)
        cdata = data.GetCellData()
        self.assertEqual(cdata.GetNumberOfArrays(), 2)
        self.assertEqual(cdata.GetNumberOfComponents(), 2)
        self.assertEqual(cdata.GetNumberOfTuples(), 1600)
        self.assertEqual(cdata.GetArray(0).GetName(), 'elemental')
        self.assertEqual(cdata.GetArray(1).GetName(), 'ObjectId')
        rng = cdata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -7.453831277231767)
        self.assertAlmostEqual(rng[1], 7.453831277231767)

        ndata = data.GetPointData()
        self.assertEqual(ndata.GetNumberOfArrays(), 1)
        self.assertEqual(ndata.GetNumberOfComponents(), 1)
        self.assertEqual(ndata.GetNumberOfTuples(), 1681)
        self.assertEqual(ndata.GetArray(0).GetName(), 'nodal')
        rng = ndata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -7.5)
        self.assertAlmostEqual(rng[1], 7.5)

        self.assertEqual(reader.getGlobalData('global'), 7.5)

        # Time = 2.25
        reader.setOptions(time=2.25)
        reader.Update()
        data = reader.GetOutputDataObject(0).GetBlock(0).GetBlock(0)
        cdata = data.GetCellData()
        self.assertEqual(cdata.GetNumberOfArrays(), 2)
        self.assertEqual(cdata.GetNumberOfComponents(), 2)
        self.assertEqual(cdata.GetNumberOfTuples(), 1600)
        self.assertEqual(cdata.GetArray(0).GetName(), 'elemental')
        self.assertEqual(cdata.GetArray(1).GetName(), 'ObjectId')
        rng = cdata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -2.23614938316953)
        self.assertAlmostEqual(rng[1], 2.23614938316953)

        ndata = data.GetPointData()
        self.assertEqual(ndata.GetNumberOfArrays(), 1)
        self.assertEqual(ndata.GetNumberOfComponents(), 1)
        self.assertEqual(ndata.GetNumberOfTuples(), 1681)
        self.assertEqual(ndata.GetArray(0).GetName(), 'nodal')
        rng = ndata.GetArray(0).GetRange()
        self.assertAlmostEqual(rng[0], -2.25)
        self.assertAlmostEqual(rng[1], 2.25)

        self.assertEqual(reader.getGlobalData('global'), 2.25)

    def testSingleFieldData(self):
        """
        Test that field data can be accessed.
        """
        reader = chigger.exodus.ExodusReader(self.single, variables=('func_pp',))
        for i, r in enumerate(range(0,21,2)):
            reader.setOptions(timestep=i)
            self.assertAlmostEqual(reader.getGlobalData('func_pp'), r/10.)

    def testVector(self):
        """
        Test that vector data can be read.
        """
        reader = chigger.exodus.ExodusReader(self.vector)
        variables = reader.getVariableInformation()
        self.assertEqual([v.name for v in variables], ['u', 'vel_'])
        self.assertEqual(variables[1].num_components, 2)

    def testAdaptivity(self):
        """
        Test that adaptive timestep files load correctly.
        """
        reader = chigger.exodus.ExodusReader(self.multiple, time_interpolation=False)

        # Times
        self.assertEqual(reader.getTimes(), [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5])

        # Time
        reader.setOptions(timestep=None, time=1.01)
        tdata, tdata1 = reader.getTimeInformation()
        self.assertIsNone(tdata1)
        self.assertAlmostEqual(tdata.time, 1)
        self.assertEqual(tdata.timestep, 2)
        self.assertEqual(tdata.index, 0)
        self.assertEqual(tdata.filename, self.multiple + '-s002')

        # Wait and then "update" the first few files
        time.sleep(1.5)
        for i in range(6):
            mooseutils.touch(self.testfiles[i])

        reader.setOptions(time=None, timestep=-1)
        tdata, tdata1 = reader.getTimeInformation()
        self.assertIsNone(tdata1)
        self.assertEqual(reader.getTimes(), [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        self.assertAlmostEqual(tdata.time, 3.0)
        self.assertEqual(tdata.timestep, 6)
        self.assertEqual(tdata.index, 0)
        self.assertEqual(tdata.filename, self.multiple + '-s006')

    def testErrors(self):
        """
        Test for error messages.
        """
        # Invalid filename
        with self.assertRaisesRegex(IOError, 'The file foo.e is not a valid filename.'):
            chigger.exodus.ExodusReader('foo.e')

        reader = chigger.exodus.ExodusReader(self.single, variables=('convected', 'func_pp'))
        logger = getattr(reader, '__log', logging.getLogger(reader.__class__.__name__))
        with self.assertLogs(logger) as l:
            reader.getGlobalData('convected')
        self.assertIn("The supplied global variable, 'convected', does not ", l.output[0])

    def testReload(self):
        """
        Test the file reloading is working.
        """
        filenames = ['../input/diffusion_1.e', '../input/diffusion_2.e']
        common = 'common.e'
        shutil.copy(filenames[0], common)
        reader = chigger.exodus.ExodusReader(common)
        self.assertEqual(reader.getTimes(), [0.0, 0.1])

        shutil.copy(filenames[1], common)
        self.assertEqual(reader.getTimes(), [0.0, 0.1, 0.2])

        shutil.copy(filenames[0], common)
        self.assertEqual(reader.getTimes(), [0.0, 0.1])

    def testVariableReload(self):
        filenames = ['../input/simple_diffusion_out.e', '../input/simple_diffusion_new_var_out.e']
        common = 'common.e'
        shutil.copy(filenames[0], common)
        reader = chigger.exodus.ExodusReader(common)
        variables = reader.getVariableInformation()
        self.assertIn('aux', [v.name for v in variables])
        self.assertIn('u', [v.name for v in variables])
        self.assertNotIn('New_0', [v.name for v in variables])

        time.sleep(1.5) # make sure modified time is different (MacOS requires > 1s)
        shutil.copy(filenames[1], common)
        variables = reader.getVariableInformation()
        self.assertIn('aux', [v.name for v in variables])
        self.assertIn('u', [v.name for v in variables])
        self.assertIn('New_0', [v.name for v in variables])

    def testVariableNameDuplicate(self):

        # Basic read
        reader = chigger.exodus.ExodusReader(self.duplicate)
        variables = reader.getVariableInformation()
        self.assertEqual(len(variables), 3)

        self.assertEqual(variables[0].name, 'variable')
        self.assertEqual(variables[0].fullname, 'variable::ELEMENTAL')
        self.assertEqual(variables[0].num_components, 1)
        self.assertEqual(variables[0].object_type, chigger.exodus.ExodusReader.ELEMENTAL)
        self.assertTrue(variables[0].active)

        self.assertEqual(variables[1].name, 'variable')
        self.assertEqual(variables[1].fullname, 'variable::GLOBAL')
        self.assertEqual(variables[1].num_components, 1)
        self.assertEqual(variables[1].object_type, chigger.exodus.ExodusReader.GLOBAL)
        self.assertTrue(variables[1].active)

        self.assertEqual(variables[2].name, 'variable')
        self.assertEqual(variables[2].fullname, 'variable::NODAL')
        self.assertEqual(variables[2].num_components, 1)
        self.assertEqual(variables[2].object_type, chigger.exodus.ExodusReader.NODAL)
        self.assertTrue(variables[2].active)

        # Check for warning if just 'variables' is provided
        logger = getattr(reader, '__log', logging.getLogger(reader.__class__.__name__))
        with self.assertLogs(logger) as l:
            reader.setOptions(variables=('variable',))
            variables = reader.getVariableInformation()
        self.assertIn("The variable name 'variable' exists with", l.output[0])

        # Check active state with suffix supplied
        reader.setOptions(variables=('variable::NODAL',))
        variables = reader.getVariableInformation()
        self.assertFalse(variables[0].active)
        self.assertFalse(variables[1].active)
        self.assertTrue(variables[2].active)

        # Check for error if bad suffix given
        with self.assertLogs(logger) as l:
            reader.setOptions(variables=('variable::WRONG',))
            variables = reader.getVariableInformation()
        self.assertIn("Unknown variable prefix '::WRONG'", l.output[0])


if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
