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
import os
import collections
import bisect
import contextlib
import fcntl
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

import mooseutils
from .. import utils
from .. import base

@contextlib.contextmanager
def lock_file(filename):
    """
    Locks a file so that the exodus reader can safely read
    a file without MOOSE writing to it while we do it.
    """
    with open(filename, "a+") as f: # "a+" to make sure it gets created
        fcntl.flock(f, fcntl.LOCK_SH)
        yield
        fcntl.flock(f, fcntl.LOCK_UN)

class ExodusReader(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):
    """
    A reader for an ExodusII file.

    This class automatically handles the adaptivity files names as follows:
        file.e, file.e-s002, file.e-s003, etc.

    Additionally, it also investigates the modified times of the file(s) so that adaptive files that
    are older do not get loaded with newer data.
    """

    # The vtkMultiBlockDataSet stored by vtkExodusIIReader has 8 data blocks, each data block is
    # associated with a different connectivity type. This list contains a list of enums used by VTK
    # to make the linkage between the connectivity and the point/field data stored.
    #
    # vtkThe MultiBlockDataSet (vtkExodusIIReader::GetOutput()) is ordered according to
    # vtkExodusIIReader::cont_types, which is the order used here.
    MULTIBLOCK_INDEX_TO_OBJECTTYPE = [vtk.vtkExodusIIReader.ELEM_BLOCK, # 0 (MOOSE Subdomains)
                                      vtk.vtkExodusIIReader.FACE_BLOCK, # 1
                                      vtk.vtkExodusIIReader.EDGE_BLOCK, # 2
                                      vtk.vtkExodusIIReader.ELEM_SET,   # 3
                                      vtk.vtkExodusIIReader.SIDE_SET,   # 4 (MOOSE Boundaries)
                                      vtk.vtkExodusIIReader.FACE_SET,   # 5
                                      vtk.vtkExodusIIReader.EDGE_SET,   # 6
                                      vtk.vtkExodusIIReader.NODE_SET]   # 7 (MOOSE Nodesets)

    # "Enum" values for Subdomains, Sidesets, and Nodesets
    BLOCK = vtk.vtkExodusIIReader.ELEM_BLOCK
    SIDESET = vtk.vtkExodusIIReader.SIDE_SET
    BOUNDARY = vtk.vtkExodusIIReader.SIDE_SET
    NODESET = vtk.vtkExodusIIReader.NODE_SET
    BLOCK_TYPES = [BLOCK, SIDESET, NODESET]

    # "Enum" values for Variable Types
    NODAL = vtk.vtkExodusIIReader.NODAL
    ELEMENTAL = vtk.vtkExodusIIReader.ELEM_BLOCK
    GLOBAL = vtk.vtkExodusIIReader.GLOBAL
    #GLOBAL = vtk.vtkExodusIIReader.GLOBAL_TEMPORAL
    VARIABLE_TYPES = [ELEMENTAL, NODAL, GLOBAL]

    # Information data structures
    BlockInformation = collections.namedtuple('BlockInformation',
                                              ['name', 'object_type', 'object_index', 'number',
                                               'multiblock_index'])
    VariableInformation = collections.namedtuple('VariableInformation',
                                                 ['name', 'object_type',
                                                  'num_components'])
    FileInformation = collections.namedtuple('FileInformation',
                                             ['filename', 'times', 'modified', 'vtkreader'])
    TimeInformation = collections.namedtuple('TimeInformation',
                                             ['timestep', 'time', 'filename', 'index'])

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()
        opt.add('time', vtype=float,
                doc="The time to view, if not specified the 'timestep' is used.")
        opt.add("timestep", default=-1, vtype=int,
                doc="The simulation timestep, this is ignored if 'time' is set (-1 for latest.)")
        opt.add("adaptive", default=True, vtype=bool,
                doc="Load adaptive files (*.e-s* files).")
        opt.add('time_interpolation', default=True, vtype=bool,
                doc="Enable/disable automatic time interpolation.")
        opt.add('displacements', default=True, vtype=bool,
                doc="Enable the viewing of displacements.")
        opt.add('displacement_magnitude', default=1.0, vtype=float,
                doc="The displacement magnitude vector.")
        opt.add('variables', vtype=str, array=True,
                doc="A tuple of  active variables, if not specified all variables are loaded.")
        #opt.add('nodeset', doc="A list of nodeset ids or names to display, use [] to display all "
        #                       "nodesets.", vtype=list)
        #opt.add('boundary', doc="A list of boundary ids (sideset) ids or names to display, use "
        #                        "[] to display all sidesets", vtype=list)
        #opt.add('block', default=[], vtype=list,
        #        doc="A list of subdomain (block) ids or names to display, by default if "
        #            "'nodeset' and 'sideset' are not specified all blocks are shown.")
        opt.add('squeeze', default=False,
                doc="Calls SetSqueezePoints on vtkExodusIIReader, according to the "
                    "VTK documentation setting this to False should be faster.")
        return opt

    def __init__(self, filename, **kwargs):
        base.ChiggerAlgorithm.__init__(self,
                                       **kwargs)
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=0, nOutputPorts=1,
                                        outputType='vtkMultiBlockDataSet')

        # Set the filename for the reader.
        self.__filename = filename
        if not os.path.isfile(self.__filename):
            raise IOError("The file {} is not a valid filename.".format(self.__filename))

        self.__active = None                               # see utils.get_active_filenames
        self.__timeinfo = []                               # all the TimeInformation objects
        self.__fileinfo = collections.OrderedDict()        # sorted FileInformation objects
        self.__blockinfo = set()                           # BlockInformation objects
        self.__variableinfo = None                         # VariableInformation objects
        self.__active_variables = set()                    # Variables from 'variables' option

    def RequestInformation(self, request, inInfo, outInfo):
        """
        (VTK Method) This is called when the VTK UpdateInformation() method is called.

        !!! DO NOT CALL THIS METHOD !!!
        """
        self.__updateActiveFilenames()
        self.__updateInformation()
        return 1

    def RequestData(self, request, inInfo, outInfo):
        """
        (VTK Method) This is called when the VTK Update() method is called.

        !!! DO NOT CALL THIS METHOD !!!
        """
        vtkobject = None

        # Initialize the current time data
        time0, time1 = self.__getTimeInformation()

        # Time Interpolation
        if (time0 is not None) and (time1 is not None):
            file0 = self.__fileinfo[time0.filename]
            file1 = self.__fileinfo[time1.filename]

            # Interpolation on same file
            if file0.vtkreader is file1.vtkreader:
                self.__updateOptions(file0.vtkreader)

                vtkobject = vtk.vtkTemporalInterpolator()
                vtkobject.SetInputConnection(0, file0.vtkreader.GetOutputPort(0))
                vtkobject.UpdateTimeStep(self.getOption('time'))

            # Interpolation across files
            else:
                self.log("Support for time interpolation across adaptive time steps is not supported.",
                         level='CRITICAL')
                return 0

        elif (time0 is not None):
            vtkobject = self.__fileinfo[time0.filename].vtkreader
            vtkobject.SetTimeStep(time0.index)
            self.__updateOptions(vtkobject)

        # Update the Reader and output port
        vtkobject.Update()
        out_data = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        out_data.ShallowCopy(vtkobject.GetOutputDataObject(0))
        return 1

    def getFilename(self):
        """
        Return the filename supplied to this reader.
        """
        return self.__filename

    def getTimes(self):
        """
        All times for the current Exodus file(s). (public)

        Returns:
            list: A list of all times.
        """
        self.__updateActiveFilenames()
        self.UpdateInformation()
        return [t.time for t in self.__timeinfo if t.time != None]

    def getGlobalData(self, variable):
        """
        Access the global (i.e., Postprocessor) data contained in the Exodus file. (public)

        Inputs:
            variable[str]: An available and active (in 'variables' setting) GLOBAL variable name.

        Returns:
            float: The global data (Postprocessor value) for the current timestep and defined
                   variable.
        """
        self.__updateActiveFilenames()
        self.UpdateInformation()
        self.Update()

        if not self.__hasVariable(self.GLOBAL, variable):
            self.log("The supplied global variable, '{}', does not exist in {}.", variable,
                     self.__filename, level='ERROR')
            return sys.float_info.min

        time0, time1 = self.__getTimeInformation()
        # Time Interpolation
        if (time0 is not None) and (time1 is not None):
            file0 = self.__fileinfo[time0.filename]
            file1 = self.__fileinfo[time1.filename]

            vtkobject0 = self.__fileinfo[time0.filename].vtkreader
            vtkobject0.SetAllArrayStatus(self.GLOBAL, 0)
            vtkobject0.SetAllArrayStatus(self.ELEMENTAL, 0)
            vtkobject0.SetAllArrayStatus(self.NODAL, 0)
            vtkobject0.SetGlobalResultArrayStatus(variable, 1)

            vtkobject1 = self.__fileinfo[time1.filename].vtkreader
            vtkobject1.SetAllArrayStatus(self.GLOBAL, 0)
            vtkobject1.SetAllArrayStatus(self.ELEMENTAL, 0)
            vtkobject1.SetAllArrayStatus(self.NODAL, 0)
            vtkobject1.SetGlobalResultArrayStatus(variable, 1)

            vtkobject0.Update()
            g0 = vtkobject0.GetOutput().GetBlock(0).GetBlock(0).GetFieldData().GetAbstractArray(variable).GetComponent(time0.index, 0)

            vtkobject1.Update()
            g1 = vtkobject1.GetOutput().GetBlock(0).GetBlock(0).GetFieldData().GetAbstractArray(variable).GetComponent(time1.index, 0)

            return utils.interp(self.getOption('time'), [time0.time, time1.time], [g0, g1])

        elif (time0 is not None):
            vtkobject = self.__fileinfo[time0.filename].vtkreader
            vtkobject.SetTimeStep(time0.index)

            vtkobject.SetAllArrayStatus(self.GLOBAL, 1)

            #vtkobject.SetAllArrayStatus(self.ELEMENTAL, 0)
            #vtkobject.SetAllArrayStatus(self.NODAL, 0)
            #vtkobject.SetGlobalResultArrayStatus(variable, 1)
            print(time0.filename)
            print(self.getVariableInformation())
            print(vtkobject.GetOutput().GetBlock(0).GetBlock(0).GetFieldData())
            print(vtkobject.GetOutput())
            g0 = vtkobject.GetOutput().GetBlock(0).GetBlock(0).GetFieldData().GetAbstractArray(variable).GetComponent(time0.index, 0)
            return g0

    def getTimeInformation(self):
        """
        The current time information. (public)

        Returns:
            tuple(): The returned tuple() has two entries, the first entry will contain a
                     collections.namedtuple with the current timestep, time, filename and local
                     time index for the file. If the supplied option "time" or "timestep" is between
                     the times available in the data then a second value will be returned, where
                     the two information objects contain the information for the two data sets
                     that will be used for interpolation.
        """
        self.__updateActiveFilenames()
        self.UpdateInformation()
        return self.__getTimeInformation()

    def getBlockInformation(self):
        """
        Get the block (subdomain, nodeset, sideset) information. (public)

        Inputs:
            check[bool]: (Default: True) When True, perform an update check and raise an exception
                                         if object is not up-to-date. This should not be used.

        Returns:
            set: BlockInformation objects for all data types in this object (keys are "enum" values
                 found in ExodusReader.MULTIBLOCK_INDEX_TO_OBJECTTYPE)
        """
        self.__updateActiveFilenames()
        self.UpdateInformation()
        blockinfo = collections.defaultdict(dict)
        for info in self.__blockinfo:
            blockinfo[info.object_type][info.number] = info

        return blockinfo

    def getVariableInformation(self, var_types=None):
        """
        Information on available variables. (public)

        Inputs:
            var_types[list]: List of variable types to return (default: ExodusReader.VARIABLE_TYPES)

        Returns:
            OrderedDict: VariableInformation objects for all variables in the file.
        """
        self.__updateActiveFilenames()
        self.UpdateInformation()

        if var_types is None:
            var_types = ExodusReader.VARIABLE_TYPES

        variables = collections.OrderedDict()
        for name, var in self.__variableinfo.items():
            if var.object_type in var_types:
                variables[name] = var
        return variables

    def __hasVariable(self, var_type, var_name):
        """
        Return True if the supplied variable name for the given type exists.
        """
        return var_name in self.getVariableInformation((var_type,))

    def __getTimeInformation(self):
        """
        Helper for getting the current TimeData object using the 'time' and 'timestep' options.
        (private)

        Returns:
            TimeData: The current TimeData object.
        """
        time = self.getOption('time')
        timestep = self.getOption('timestep')

        # Timestep
        n = len(self.__timeinfo) - 1
        if time is not None:
            times = [t.time for t in self.__timeinfo]

            # Error if supplied time is out of range
            if (time > times[-1]) or (time < times[0]):
                mooseutils.mooseWarning("Time out of range,", time, "not in",
                                        repr([times[0], times[-1]]), ", using the latest timestep.")

            # Exact match
            try:
                idx = times.index(time)
                return self.__timeinfo[idx], None
            except ValueError:
                pass

            # Locate index less than or equal to the desired time
            idx = bisect.bisect_right(times, time) - 1
            if self.getOption('time_interpolation'):
                return self.__timeinfo[idx], self.__timeinfo[idx+1]
            else:
                return self.__timeinfo[idx], None

        elif timestep is not None:

            # Account for out-of-range timesteps
            idx = timestep
            if (timestep < 0) and (timestep != -1):
                self.log("Timestep out of range: {} not in {}.", timestep, repr([0, n]), level='WARNING')
                self.setOption('timestep', 0)
                idx = 0
            elif (timestep > n) or (timestep == -1):
                if timestep != -1:
                    self.log("Timestep out of range: {} not in {}.", timestep, repr([0, n]), level='WARNING')
                self.setOption('timestep', n)
                idx = n

            return self.__timeinfo[idx], None

        # Default to last timestep
        return self.__timeinfo[-1], None

    def applyOptions(self):
        """
        """
        super(ExodusReader, self).applyOptions()

        variables = self.getOption('variables')
        self.__active_variables = collections.defaultdict(set)
        if variables is not None:
            for var in variables:
                self.__updateActiveVariable(var)

    def __updateActiveVariable(self, var):

        var_types = ExodusReader.VARIABLE_TYPES
        x = var.split("::")
        if (len(x) == 2) and (x[1] == 'NODAL'):
            var_types = [ExodusReader.NODAL]
        elif (len(x) == 2) and (x[1] == 'ELEMENTAL'):
            var_types = [ExodusReader.ELEMENTAL]
        elif (len(x) == 2) and (x[1] == 'GLOBAL'):
            var_types = [ExodusReader.GLOBAL]
        elif len(x) == 2:
            self.log("Unknown variable prefix '::{}', must be 'NODAL', 'ELEMENTAL', or 'GLOBAL'", x[1], level='ERROR')

        for vtype in var_types:
            if self.__hasVariable(vtype, var):
                self.__active_variables[var].add(vtype)

        for name, vtype in self.__active_variables:
            if len(vtype) > 1:
                self.log("The variable name '{}' is used to represent multiple data types, use the '::NODAL', '::ELEMENTAL', or '::GLOBAL' prefix to limit the loading to a certain type.", var, level='WARNING')

    def __updateOptions(self, vtkreader):
        """
        (Private) Apply options to the supplied vtkExodusIIReader.

        This method is needed because in some instances when temporal interpolation occurs two
        separate objects are used.
        """

        # Displacement Settings
        vtkreader.SetApplyDisplacements(self.getOption('displacements'))
        vtkreader.SetDisplacementMagnitude(self.getOption('displacement_magnitude'))

        ## Set the geometric objects to load (i.e., subdomains, nodesets, sidesets)
        #active_blockinfo = self.__getActiveBlocks()
        #for data in self.__blockinfo:
        #    if (not active_blockinfo) or (data in active_blockinfo):
        #        vtkreader.SetObjectStatus(data.object_type, data.object_index, 1)
        #    else:
        #        vtkreader.SetObjectStatus(data.object_type, data.object_index, 0)

        # According to the VTK documentation setting this to False (not the default) speeds
        # up data loading. In my testing I was seeing load times cut in half or more with
        # "squeezing" disabled. I am leaving this as an option just in case we discover some
        # reason it shouldn't be disabled.
        vtkreader.SetSqueezePoints(self.getOption('squeeze'))

        # Set the data arrays to load
        #
        # If the object has not been initialized then all of the variables should be enabled
        # so that the block and variable information are complete when populated. After this
        # only the variables listed in the 'variables' options, if any, are activated, which
        # reduces loading times. If 'variables' is not given, all the variables are loaded.
        #if self.__active_variables:
        #    self.SetAllArrayStatus(ExodusReader.NODAL, 0)
        #    self.SetAllArrayStatus(ExodusReader.ELEMENTAL, 0)
        #    self.SetAllArrayStatus(ExodusReader.GLOBAL, 0)
        #    for var, vtypes in self.__active_variables.items():
        #        for vtype in vtypes:
        #            vtkreader.SetObjectArrayStatus(vtype, var, 1)

    def __updateActiveFilenames(self):
        filenames = self.__getActiveFilenames()
        if self.__active != filenames:
            self.__active = filenames
            self.Modified()

    def __getActiveFilenames(self):
        """
        The active ExodusII file(s). (private)

        Returns:
            list: Contains tuples (filename, modified time) of active file(s).
        """
        if self.getOption('adaptive'):
            return utils.get_active_filenames(self.__filename, self.__filename + '-s*')
        else:
            return utils.get_active_filenames(self.__filename)

    def __getActiveBlocks(self):
        """
        Get a list of active blocks/boundary/nodesets. (private)

        Returns an empty list if all should be enabled.
        """
        output = []
        for param in ['block', 'boundary', 'nodeset']:
            blocks = self.getOption(param)
            if blocks is not None:
                for data in self.__blockinfo:
                    if data.name in blocks:
                        output.append(data)
        return output

    def __updateInformation(self):
        """
        Update file, time, block, and variable information.
        """
        # Re-move any old files in timeinfo dict()
        for fname in list(self.__fileinfo.keys()):
            if fname not in self.__active:
                self.__fileinfo.pop(fname)

        # Loop through each file and determine the times
        key = vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS()
        for filename, current_modified in self.__active:

            tinfo = self.__fileinfo.get(filename, None)
            if tinfo and (tinfo.modified == current_modified):
                continue

            with lock_file(filename):
                vtkreader = vtk.vtkExodusIIReader()
                vtkreader.SetFileName(filename)
                vtkreader.UpdateInformation()

                vtkinfo = vtkreader.GetExecutive().GetOutputInformation(0)
                steps = range(vtkreader.GetNumberOfTimeSteps())
                times = [vtkinfo.Get(key, i) for i in steps]

                if not times:
                    times = [None] # When --mesh-only is used, not time information is written
                self.__fileinfo[filename] = ExodusReader.FileInformation(filename=filename,
                                                                         times=times,
                                                                         modified=current_modified,
                                                                         vtkreader=vtkreader)

        # Create a TimeInformation object for each timestep that indicates the correct file.
        self.__timeinfo = []
        timestep = 0
        for tinfo in self.__fileinfo.values():
            for i, t in enumerate(tinfo.times):
                tdata = ExodusReader.TimeInformation(timestep=timestep, time=t,
                                                     filename=tinfo.filename,
                                                     index=i)
                self.__timeinfo.append(tdata)
                timestep += 1

        # Queries the base file for the subdomain, sideset, nodeset, and variable, it is assumed
        # that all files contain the same variables and blocks, as it should.
        with lock_file(self.__filename):
            index = 0 # Index to be used with the vtkExtractBlock::AddIndex method

            vtkreader = vtk.vtkExodusIIReader()
            vtkreader.SetFileName(self.__filename)
            vtkreader.UpdateInformation()

            # Loop over all blocks of the vtk.MultiBlockDataSet
            for obj_type in ExodusReader.MULTIBLOCK_INDEX_TO_OBJECTTYPE:
                index += 1
                for j in range(vtkreader.GetNumberOfObjects(obj_type)):
                    index += 1
                    name = vtkreader.GetObjectName(obj_type, j)
                    vtkid = str(vtkreader.GetObjectId(obj_type, j))
                    if name.startswith('Unnamed'):
                        name = vtkid

                    binfo = ExodusReader.BlockInformation(object_type=obj_type,
                                                          name=name,
                                                          number=vtkid,
                                                          object_index=j,
                                                          multiblock_index=index)
                    self.__blockinfo.add(binfo)

            # Loop over all variable types
            unsorted = dict()
            for variable_type in ExodusReader.VARIABLE_TYPES:
                for i in range(vtkreader.GetNumberOfObjectArrays(variable_type)):
                    var_name = vtkreader.GetObjectArrayName(variable_type, i)
                    if var_name is not None:
                        num = vtkreader.GetNumberOfObjectArrayComponents(variable_type, i)
                        vinfo = ExodusReader.VariableInformation(name=var_name,
                                                                 object_type=variable_type,
                                                                 num_components=num)
                        unsorted[var_name] = vinfo

            self.__variableinfo = collections.OrderedDict(sorted(unsorted.items(),
                                                                 key=lambda x: x[0].lower()))
