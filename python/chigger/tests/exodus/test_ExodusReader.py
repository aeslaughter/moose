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
import vtk

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

    def testCreateDelete(self):
        """Test that creating and deleting an object calls correct methods."""
        # Create ExodusReader
        with self.assertLogs(level=logging.DEBUG) as l:
            reader = chigger.exodus.ExodusReader(self.single)

        self.assertEqual(len(l.output), 2)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOptions::Modified')

        # Delete the object
        with self.assertLogs(level=logging.DEBUG) as l:
            del reader
        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: __del__()')

    def testOptions(self):
        """Test the setting options calls the correct methods."""

        # Create ExodusReader
        reader = chigger.exodus.ExodusReader(self.single)

        # Test setOption
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOption('timestep', 2)
            reader.updateInformation()

        self.assertEqual(len(l.output), 11)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOption')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOption::Modified')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateFileInformation')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateTimeInformation')
        self.assertEqual(l.output[7], 'DEBUG:ExodusReader: __updateBlockInformation')
        self.assertEqual(l.output[8], 'DEBUG:ExodusReader: __updateVariableInformation')
        self.assertEqual(l.output[9], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[10], 'DEBUG:ExodusReader: __updateActiveVariables')

        # Test setOption, that doesn't change options
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOption('timestep', 2)
            reader.updateInformation()

        self.assertEqual(len(l.output), 2)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOption')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: updateInformation')

        # Test setOptions
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOptions(timestep=3)
            reader.updateInformation()

        self.assertEqual(len(l.output), 7)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOptions::Modified')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateActiveVariables')

        # Test setOptions, that doesn't change options
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOptions(timestep=3)
            reader.updateInformation()

        self.assertEqual(len(l.output), 2)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: updateInformation')


    def testFileInformation(self):
        """Test that the file information is updated correctly."""

        # Create ExodusReader
        reader = chigger.exodus.ExodusReader(self.single)

        # Get FileInfo dict, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            finfo = reader.getFileInformation()

        self.assertEqual(len(l.output), 9)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: __updateFileInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: __updateTimeInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateBlockInformation')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateVariableInformation')
        self.assertEqual(l.output[7], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[8], 'DEBUG:ExodusReader: __updateActiveVariables')

        # Get FileInfo dict, this should NOT trigger a call to the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            finfo = reader.getFileInformation()

        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')

        # Delete the object
        with self.assertLogs(level=logging.DEBUG) as l:
            del reader
        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: __del__()')

        # Check that the file information is valid
        self.assertEqual(len(finfo), 1)
        self.assertIn(self.single, finfo)

        f = finfo[self.single]
        self.assertEqual(f.filename, self.single)
        self.assertEqual(len(f.times), 21)

    def testTimeInformation(self):
        """Test the TimeInfo objects"""

        # Create ExodusReader
        reader = chigger.exodus.ExodusReader(self.single)

        # Get TimeInfo list, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            tinfo = reader.getTimeInformation()

        self.assertEqual(len(l.output), 9)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: __updateFileInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: __updateTimeInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateBlockInformation')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateVariableInformation')
        self.assertEqual(l.output[7], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[8], 'DEBUG:ExodusReader: __updateActiveVariables')

        # Get TimeInfo list, this should NOT trigger a call to the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            tinfo = reader.getTimeInformation()

        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')

        self.assertEqual(len(tinfo), 21)
        self.assertEqual(tinfo[0].timestep, 0)
        self.assertEqual(tinfo[0].time, 0.0)
        self.assertEqual(tinfo[0].filename, self.single)
        self.assertEqual(tinfo[0].index, 0)

        self.assertEqual(tinfo[9].timestep, 9)
        self.assertAlmostEqual(tinfo[9].time, 0.9)
        self.assertEqual(tinfo[9].filename, self.single)
        self.assertEqual(tinfo[9].index, 9)

    def testCurrentTimeInformation(self):
        """Test the returning of the current TimeInfo objects"""

        # Create ExodusReader
        reader = chigger.exodus.ExodusReader(self.single)

        # Get TimeInfo tuple, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            tinfo = reader.getCurrentTimeInformation()

        self.assertEqual(len(l.output), 9)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: __updateFileInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: __updateTimeInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateBlockInformation')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateVariableInformation')
        self.assertEqual(l.output[7], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[8], 'DEBUG:ExodusReader: __updateActiveVariables')

        # Get TimeInfo tuple, this should NOT trigger a call to the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            tinfo = reader.getCurrentTimeInformation()

        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')

        self.assertEqual(len(tinfo), 2)
        self.assertIsNone(tinfo[1])
        self.assertEqual(tinfo[0].timestep, 20)
        self.assertAlmostEqual(tinfo[0].time, 2)
        self.assertEqual(tinfo[0].filename, self.single)
        self.assertEqual(tinfo[0].index, 20)

        # Change the time, the __update* methods should NOT be called because the files didn't change
        reader.setOption('time', 1)
        with self.assertLogs(level=logging.DEBUG) as l:
            tinfo = reader.getCurrentTimeInformation()

        self.assertEqual(len(l.output), 5)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: __updateActiveVariables')

        self.assertEqual(len(tinfo), 2)
        self.assertEqual(tinfo[0].timestep, 10)
        self.assertAlmostEqual(tinfo[0].time, 1)
        self.assertEqual(tinfo[0].filename, self.single)
        self.assertEqual(tinfo[0].index, 10)

        self.assertEqual(tinfo[1].timestep, 11)
        self.assertAlmostEqual(tinfo[1].time, 1.1)
        self.assertEqual(tinfo[1].filename, self.single)
        self.assertEqual(tinfo[1].index, 11)

    def testBlockInformation(self):
        """Test the BlockInfo objects"""

        # Create ExodusReader
        with self.assertLogs(level=logging.DEBUG) as l:
            reader = chigger.exodus.ExodusReader(self.single)

        # Get BlockInfo dict, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            binfo = reader.getBlockInformation()

        self.assertEqual(len(l.output), 9)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: __updateFileInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: __updateTimeInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateBlockInformation')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateVariableInformation')
        self.assertEqual(l.output[7], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[8], 'DEBUG:ExodusReader: __updateActiveVariables')

        # Get BlockInfo dict, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            binfo = reader.getBlockInformation()

        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')

        self.assertEqual(len(binfo), 3)

        blk_binfo = binfo[chigger.exodus.ExodusReader.BLOCK]
        self.assertEqual(len(blk_binfo), 2)
        self.assertEqual(blk_binfo[0].name, '1')
        self.assertEqual(blk_binfo[0].number, 1)
        self.assertEqual(blk_binfo[0].object_type, chigger.exodus.ExodusReader.BLOCK)
        self.assertEqual(blk_binfo[0].object_index, 0)
        self.assertEqual(blk_binfo[0].multiblock_index, 2)
        self.assertTrue(blk_binfo[0].active)

        self.assertEqual(blk_binfo[1].name, '76')
        self.assertEqual(blk_binfo[1].number, 76)
        self.assertEqual(blk_binfo[1].object_type, chigger.exodus.ExodusReader.BLOCK)
        self.assertEqual(blk_binfo[1].object_index, 1)
        self.assertEqual(blk_binfo[1].multiblock_index, 3)
        self.assertTrue(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.SIDESET]
        self.assertEqual(len(blk_binfo), 2)
        self.assertEqual(blk_binfo[0].name, 'bottom')
        self.assertEqual(blk_binfo[0].number, 1)
        self.assertEqual(blk_binfo[0].object_type, chigger.exodus.ExodusReader.SIDESET)
        self.assertEqual(blk_binfo[0].object_index, 0)
        self.assertEqual(blk_binfo[0].multiblock_index, 8)
        self.assertTrue(blk_binfo[0].active)

        self.assertEqual(blk_binfo[1].name, 'top')
        self.assertEqual(blk_binfo[1].number, 2)
        self.assertEqual(blk_binfo[1].object_type, chigger.exodus.ExodusReader.SIDESET)
        self.assertEqual(blk_binfo[1].object_index, 1)
        self.assertEqual(blk_binfo[1].multiblock_index, 9)
        self.assertTrue(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.NODESET]
        self.assertEqual(len(blk_binfo), 2)
        self.assertEqual(blk_binfo[0].name, '1')
        self.assertEqual(blk_binfo[0].number, 1)
        self.assertEqual(blk_binfo[0].object_type, chigger.exodus.ExodusReader.NODESET)
        self.assertEqual(blk_binfo[0].object_index, 0)
        self.assertEqual(blk_binfo[0].multiblock_index, 13)
        self.assertTrue(blk_binfo[0].active)

        self.assertEqual(blk_binfo[1].name, '2')
        self.assertEqual(blk_binfo[1].number, 2)
        self.assertEqual(blk_binfo[1].object_type, chigger.exodus.ExodusReader.NODESET)
        self.assertEqual(blk_binfo[1].object_index, 1)
        self.assertEqual(blk_binfo[1].multiblock_index, 14)
        self.assertTrue(blk_binfo[1].active)

        # Test setting 'blocks'
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOptions(blocks=[1])
            binfo = reader.getBlockInformation()

        self.assertEqual(len(l.output), 7)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOptions::Modified')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateActiveVariables')

        blk_binfo = binfo[chigger.exodus.ExodusReader.BLOCK]
        self.assertTrue(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.SIDESET]
        self.assertFalse(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.NODESET]
        self.assertFalse(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        with self.assertLogs(level=logging.DEBUG) as l:
            reader.updateData()

        self.assertEqual(len(l.output), 3)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateData')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestData')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: _onRequestData')

        tinfo, _ = reader.getCurrentTimeInformation()
        vtkreader = reader.getFileInformation()[tinfo.filename].vtkreader
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 1))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 1))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 1))

        # Test setting 'nodesets'
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOptions(nodesets=[2])
            binfo = reader.getBlockInformation()

        self.assertEqual(len(l.output), 7)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOptions::Modified')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateActiveVariables')

        blk_binfo = binfo[chigger.exodus.ExodusReader.BLOCK]
        self.assertTrue(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.SIDESET]
        self.assertFalse(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.NODESET]
        self.assertFalse(blk_binfo[0].active)
        self.assertTrue(blk_binfo[1].active)

        with self.assertLogs(level=logging.DEBUG) as l:
            reader.updateData()

        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 1))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 1))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 0))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 1))

        # Test setting 'sidesets'
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOptions(sidesets=['bottom'])
            binfo = reader.getBlockInformation()

        self.assertEqual(len(l.output), 7)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOptions::Modified')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateActiveVariables')

        blk_binfo = binfo[chigger.exodus.ExodusReader.BLOCK]
        self.assertTrue(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.SIDESET]
        self.assertTrue(blk_binfo[0].active)
        self.assertFalse(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.NODESET]
        self.assertFalse(blk_binfo[0].active)
        self.assertTrue(blk_binfo[1].active)

        with self.assertLogs(level=logging.DEBUG) as l:
            reader.updateData()

        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 1))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 0))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 1))
        self.assertFalse(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 0))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 1))

        # Test un-setting
        with self.assertLogs(level=logging.DEBUG) as l:
            reader.setOptions(blocks=None, sidesets=None, nodesets=None)
            binfo = reader.getBlockInformation()
            reader.updateData()

        self.assertEqual(len(l.output), 10)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: setOptions')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: setOptions::Modified')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: _onRequestInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateActiveBlocks')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateActiveVariables')
        self.assertEqual(l.output[7], 'DEBUG:ExodusReader: updateData')
        self.assertEqual(l.output[8], 'DEBUG:ExodusReader: RequestData')
        self.assertEqual(l.output[9], 'DEBUG:ExodusReader: _onRequestData')

        blk_binfo = binfo[chigger.exodus.ExodusReader.BLOCK]
        self.assertTrue(blk_binfo[0].active)
        self.assertTrue(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.SIDESET]
        self.assertTrue(blk_binfo[0].active)
        self.assertTrue(blk_binfo[1].active)

        blk_binfo = binfo[chigger.exodus.ExodusReader.NODESET]
        self.assertTrue(blk_binfo[0].active)
        self.assertTrue(blk_binfo[1].active)

        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 0))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 1))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 0))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.SIDE_SET, 1))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 0))
        self.assertTrue(vtkreader.GetObjectStatus(vtk.vtkExodusIIReader.NODE_SET, 1))

        # TODO: Need to test warnings


    def testVariableInformation(self):
        """Test the VarInfo objects"""

        # Create ExodusReader
        reader = chigger.exodus.ExodusReader(self.single)

        # Get VarInfo dict, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            vinfo = reader.getVariableInformation()

        self.assertEqual(len(l.output), 7)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')
        self.assertEqual(l.output[1], 'DEBUG:ExodusReader: RequestInformation')
        self.assertEqual(l.output[2], 'DEBUG:ExodusReader: onRequestInformation')
        self.assertEqual(l.output[3], 'DEBUG:ExodusReader: __updateFileInformation')
        self.assertEqual(l.output[4], 'DEBUG:ExodusReader: __updateTimeInformation')
        self.assertEqual(l.output[5], 'DEBUG:ExodusReader: __updateBlockInformation')
        self.assertEqual(l.output[6], 'DEBUG:ExodusReader: __updateVariableInformation')

        # Get BlockInfo list, this should trigger a call via the VTK pipeline RequestInformation
        with self.assertLogs(level=logging.DEBUG) as l:
            vinfo = reader.getVariableInformation()

        self.assertEqual(len(l.output), 1)
        self.assertEqual(l.output[0], 'DEBUG:ExodusReader: updateInformation')

        self.assertEqual(len(vinfo), 3)

        e_vinfo = vinfo[chigger.exodus.ExodusReader.ELEMENTAL]
        self.assertEqual(len(e_vinfo), 1)
        self.assertEqual(e_vinfo[0].name, 'aux_elem')
        self.assertEqual(e_vinfo[0].object_type, chigger.exodus.ExodusReader.ELEMENTAL)
        self.assertEqual(e_vinfo[0].num_components, 1)
        self.assertTrue(e_vinfo[0].active)

        n_vinfo = vinfo[chigger.exodus.ExodusReader.NODAL]
        self.assertEqual(len(n_vinfo), 2)
        self.assertEqual(n_vinfo[0].name, 'convected')
        self.assertEqual(n_vinfo[0].object_type, chigger.exodus.ExodusReader.NODAL)
        self.assertEqual(n_vinfo[0].num_components, 1)
        self.assertTrue(n_vinfo[0].active)

        self.assertEqual(n_vinfo[1].name, 'diffused')
        self.assertEqual(n_vinfo[1].object_type, chigger.exodus.ExodusReader.NODAL)
        self.assertEqual(n_vinfo[1].num_components, 1)
        self.assertTrue(n_vinfo[1].active)

        g_vinfo = vinfo[chigger.exodus.ExodusReader.GLOBAL]
        self.assertEqual(len(g_vinfo), 1)
        self.assertEqual(g_vinfo[0].name, 'func_pp')
        self.assertEqual(g_vinfo[0].object_type, chigger.exodus.ExodusReader.GLOBAL)
        self.assertEqual(g_vinfo[0].num_components, 1)
        self.assertTrue(g_vinfo[0].active)

        # TODO: Test 'variables=...'

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
        with self.assertLogs() as l:
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
        with self.assertLogs() as l:
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
        with self.assertLogs() as l:
            reader.setOptions(variables=('variable::WRONG',))
            variables = reader.getVariableInformation()
        self.assertIn("Unknown variable prefix '::WRONG'", l.output[0])


if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2)
