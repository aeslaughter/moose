#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
#from ExodusSource import ExodusSource
from .ExodusReader import ExodusReader
from .MultiAppExodusReader import MultiAppExodusReader
import mooseutils
from .. import base
from .. import utils
from .. import filters

@base.addFilter(filters.GeometryFilter, required=True)
@base.addFilter(filters.ExtractBlockFilter, required=True)
class ExodusSource(base.ChiggerSource):
    """
    Result object to displaying ExodusII data from a single reader.
    """
    VTKACTORTYPE = vtk.vtkActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()

        # Variable selection
        opt.add('variable', vtype=str, doc="The nodal or elemental variable to render.")
        opt.add('component', -1, vtype=int, allow=(-1, 0, 1, 2),
                doc="The vector variable component to render (-1 plots the magnitude).")

        # Data range
        opt.add('lim', vtype=float, size=2,
                doc="The range of data to display on the volume and colorbar; range takes " \
                    "precedence of min/max.")
        opt.add('local_lim', False, "Use local range when computing the default data range.")
        opt.add('min', vtype=float, doc="The minimum range.")
        opt.add('max', vtype=float, doc="The maximum range.")

        # Subdomains/sidesets/nodesets
        opt.add('nodesets', None, vtype=list,
                doc="A list of nodeset ids or names to display, use [] to display all nodesets.")
        opt.add('sidesets', None, vtype=list,
                doc="A list of sidesets (boundary) ids or names to display, use [] to display " \
                    "all sidesets.")
        opt.add('blocks', [], vtype=list,
                doc="A list of subdomain (block) ids or names to display, use [] to display all " \
                    "blocks.")

        opt.add('representation', 'surface', allow=('volume', 'surface', 'wireframe', 'points'),
                doc="View volume representation.")

        # Colormap
        opt += base.ColorMap.validOptions()

        opt.add('explode', None, vtype=float,
                doc="When multiple sources are being used (e.g., NemesisReader) setting this to a "
                    "value will cause the various sources to be 'exploded' away from the center of "
                    "the entire object.")
        return opt

    @staticmethod
    def validKeyBindings():

        bindings = base.ChiggerSource.validKeyBindings()

        # Opacity keybindings
        bindings.add('a', ExodusSource._updateOpacity,
                     desc='Increase the alpha (opacity) by 1%.')
        bindings.add('a', ExodusSource._updateOpacity, shift=True,
                     desc='Decrease the alpha (opacity) by 1%.')

        # Colormap keybindings
        bindings.add('m', ExodusSource._updateColorMap,
                     desc="Toggle through available colormaps.")
        bindings.add('m', ExodusSource._updateColorMap, shift=True,
                     desc="Toggle through available colormaps, in reverse direction.")

        # Time keybindngs
        bindings.add('t', ExodusSource._updateTimestep,
                     desc="Increase timestep by 1.")
        bindings.add('t', ExodusSource._updateTimestep, shift=True,
                     desc="Decrease the timestep by 1.")

        return bindings

    def __init__(self, viewport, reader, **kwargs):

        self.__reader = reader
        self.__current_variable = None
        self._colormap = base.ColorMap()

        base.ChiggerSource.__init__(self, viewport,
                                    nInputPorts=1, inputType='vtkMultiBlockDataSet',
                                    nOutputPorts=1, outputType='vtkMultiBlockDataSet',
                                    **kwargs)

        self.SetInputConnection(self.__reader.GetOutputPort())


        # TODO: Check 'blocks', etc. and warn if set


    def _onRequestData(self, inInfo, outInfo):
        base.ChiggerSource._onRequestData(self, inInfo, outInfo)

        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt.ShallowCopy(inp)

    def _onRequestInformation(self):
        base.ChiggerSource._onRequestInformation(self)

        # Update the block/boundary/nodeset settings on the reader
        self.__updateActiveBlocks()

        # Update the variable settings on the reader
        self.__updateActiveVariables()


        self.__reader.updateInformation()

        # Update the block/boundary/nodeset settings to convert [] to all.
        extract_indices = []
        block_info = self.__reader.getBlockInformation()
        for binfo in block_info.values():
            for b in binfo:
                if b.active:
                    extract_indices.append(b.multiblock_index)

        fobject = self._filters['extract']
        fobject.setOption('indices', extract_indices)

        """
        # Update the block/boundary/nodeset settings to convert [] to all.
        block_info = self.__reader.getBlockInformation()
        for item in ['block', 'boundary', 'nodeset']:
            opt = self.getOption(item)
            if opt == []:
                self.setOption(item, [item.name for item in \
                                      block_info[getattr(ExodusReader, item.upper())].itervalues()])

        # Update the extract indices
        def get_indices(option, vtk_type):
            # Helper to populate vtkExtractBlock object from selected blocks/sidesets/nodesets
            indices = []
            blocks = self.getOption(option)
            if blocks:
                for vtkid, item in block_info[vtk_type].items():
                    for name in blocks:
                        if (item.name == str(name)) or (str(name) == vtkid):
                            indices.append(item.multiblock_index)
            return indices

        extract_indices = get_indices('block', ExodusReader.BLOCK)
        extract_indices += get_indices('boundary', ExodusReader.SIDESET)
        extract_indices += get_indices('nodeset', ExodusReader.NODESET)
        """


        self._vtkmapper.InterpolateScalarsBeforeMappingOn()

        #self.__updateVariable()


    def __updateActiveBlocks(self):
        self.debug('__updateActiveBlocks')

        block_info = self.__reader.getBlockInformation()
        self.__setActiveBlocksHelper('blocks', block_info[ExodusReader.BLOCK])
        self.__setActiveBlocksHelper('sidesets', block_info[ExodusReader.SIDESET])
        self.__setActiveBlocksHelper('nodesets', block_info[ExodusReader.NODESET])

    def __updateActiveVariables(self):
        self.debug('__updateActiveVariables')

        vname = self.getOption('variable')
        has_nodal = self.__reader.hasVariable(ExodusReader.NODAL, vname)
        has_elemental = self.__reader.hasVariable(ExodusReader.ELEMENTAL, vname)

        if has_nodal and has_elemental:
            self.warning("The supplied variable name '{0}' exists as both a nodal and elemental variable, use '{0}::NODAL' or '{0}::ELEMENTAL' to indicate which is desired. The nodal version is being used.", vname)
            vfullname = '{}::NODAL'.format(vname)
            self._vtkmapper.SetScalarModeToUsePointFieldData()

        elif has_nodal:
            vfullname = '{}::NODAL'.format(vname)
            self._vtkmapper.SetScalarModeToUsePointFieldData()

        elif has_elemental:
            vfullname = '{}::ELEMENTAL'.format(vname)
            self._vtkmapper.SetScalarModeToUseCellFieldData()

        else:
            vinfo = self.__reader.getVariableInformation()
            velem = ', '.join([v.name for v in vinfo[ExodusReader.ELEMENTAL]])
            vnodal = ', '.join([v.name for v in vinfo[ExodusReader.NODAL]])
            vfullname = None
            self.error("The supplied variable name '{}' does not exist on the supplied reader. The following variables are available:\n  Elemental: {}\n  Nodal: {}.", vname, velem, vnodal)


        if vfullname is not None:
            current = self.__reader.getOption('variables')
            current = current + (vfullname,) if current is not None else (vfullname,)
            self.__reader.setOption('variables', current)
            self._vtkmapper.SelectColorArray(vname)



    #def __init__(self, reader, **kwargs):
    #    base.ChiggerSource(reader, **kwargs)

    #    self._reader = reader

    #    # Build the ExodusSource objects
    #    if isinstance(reader, ExodusReader):
    #        sources = [ExodusSource(reader)]
    #    elif isinstance(reader, MultiAppExodusReader):
    #        sources = [ExodusSource(r) for r in reader]
    #    else:
    #        raise mooseutils.MooseException('The supplied object of type {} is not supported, '
    #                                        'only ExodusReader and MultiAppExodusReader objects '
    #                                        'may be utilized.'.format(reader.__class__.__name__))

    #    # Supply the sources to the base class
    #    #super(ExodusSource, self).__init__(*sources, **kwargs)

    #    self.__outline_result = None

    def __setActiveBlocksHelper(self, param, binfo):

        local = self.getOption(param)
        if local == []:
            local = tuple([b.name for b in binfo])

        if local is not None:
            self.__reader.setOption(param, self.__reader.getOption(param) + local)







    """
    def update(self, **kwargs):
        super(ExodusSource, self).update(**kwargs)

        # Update the ExodusReader objects
        self._reader.update()

        # Do not mess with the range if there is a source without a variable
        if any([src.getCurrentVariableInformation() is None for src in self._sources]):
            return

        # Re-compute ranges for all sources
        rng = list(self.getRange(local=self.getOption('local_range')))
        if self.isOptionValid('lim'):
            rng = self.getOption('lim')
        else:
            if self.isOptionValid('min'):
                rng[0] = self.getOption('min')
            if self.isOptionValid('max'):
                rng[1] = self.getOption('max')

        if rng[0] > rng[1]:
            mooseutils.mooseDebug("Minimum range greater than maximum:", rng[0], ">", rng[1],
                                  ", the range/min/max settings are being ignored.")
            rng = list(self.getRange())

        for src in self._sources:
            src.getVTKMapper().SetScalarRange(rng)

        # Explode
        if self.isOptionValid('explode'):
            factor = self.applyOption('explode')
            m = self.getCenter()
            for src in self._sources:
                c = src.getVTKActor().GetCenter()
                d = (c[0]-m[0], c[1]-m[1], c[2]-m[2])
                src.getVTKActor().AddPosition(d[0]*factor, d[1]*factor, d[2]*factor)
    """
    #def getRange(self, **kwargs):
    #    """
    #    Return the min/max range for the selected variables and blocks/boundary/nodeset.

    #    NOTE: For the range to be restricted by block/boundary/nodest the reader must have
    #          "squeeze=True", which can be much slower.
    #    """
    #    rngs = [src.getRange(**kwargs) for src in self._sources]
    #    return utils.get_min_max(*rngs)

    #def getCenter(self):
    #    """
    #    Return the center (based on the bounds) of all the objects.
    #    """
    #    b = self.getBounds()
    #    return ((b[1]-b[0])/2., (b[3]-b[2])/2., (b[5]-b[4])/2.)


    def __updateVariable(self):
        """
        Method to update the active variable to display on the object. (private)
        """
        def get_available_variables():
            """
            Returns a sting listing the available nodal and elemental variable names.
            """
            nvars = self.__reader.getVariableInformation()

            msg = []
            if nvars:
                msg += ["Nodal:"]
                msg += [" " + var.name for var in nvars]
            if evars:
                msg += ["\nElemental:"]
                msg += [" " + var.name for var in evars]
            return ''.join(msg)

        # Define the active variable name
        available = self.__reader.getVariableInformation()

        # Case when no variable exists
        if not available:
            return

        default = available[0]
        if not self.isOptionValid('variable'):
            varinfo = default
        else:
            var_name = self.getOption('variable')
            varinfo = None
            for var in available:
                if var_name in (var.name, var.fullname):
                    varinfo = var
            if varinfo is None:
                msg = "The variable '{}' provided does not exist, using '{}', available " \
                      "variables include:\n{}"
                self.warning(msg, var_name, default.name, get_available_variables())
                varinfo = default

        # Make sure the variable is active
        if not varinfo.active:
            msg = "The selected variable '{}' is not active on the ExodusReader"
            self.error(msg, varinfo.name)
            return

        # Update vtkMapper to the correct data mode
        if varinfo.object_type == ExodusReader.ELEMENTAL:
            self._vtkmapper.SetScalarModeToUseCellFieldData()
        elif varinfo.object_type == ExodusReader.NODAL:
            self._vtkmapper.SetScalarModeToUsePointFieldData()
        else:
            raise mooseutils.MooseException('Unknown variable type, not sure how you made it here.')

        self.__current_variable = varinfo

        # Colormap
        if not self.getOption('color'):
            self._colormap.setOptions(cmap=self.getOption('cmap'),
                                      cmap_reverse=self.getOption('cmap_reverse'),
                                      cmap_num_colors=self.getOption('cmap_num_colors'))
            self._vtkmapper.SelectColorArray(varinfo.name)
            self._vtkmapper.SetLookupTable(self._colormap())
            self._vtkmapper.UseLookupTableScalarRangeOff()

        # Component
        component = -1 # Default component to utilize if not valid
        if self.isOptionValid('component'):
            component = self.getOption('component')

        if component == -1:
            self._vtkmapper.GetLookupTable().SetVectorModeToMagnitude()
        else:
            if component > varinfo.num_components:
                msg = 'Invalid component number ({}), the variable "{}" has {} components.'
                mooseutils.mooseError(msg.format(component, varinfo.name, varinfo.num_components))
            self._vtkmapper.GetLookupTable().SetVectorModeToComponent()
            self._vtkmapper.GetLookupTable().SetVectorComponent(component)

        # Range
        if (self.isOptionValid('min') or self.isOptionValid('max')) and self.isOptionValid('lim'):
            self.error('Both a "min" and/or "max" options has been set along with the '
                       '"range" option, the "range" is being utilized, the others are '
                       'ignored.')

        # Range
        """
        rng = list(self.getRange(local=self.getOption('local_lim')))
        if self.isOptionValid('lim'):
            rng = self.getOption('lim')
        else:
            if self.isOptionValid('min'):
                rng[0] = self.getOption('min')
            if self.isOptionValid('max'):
                rng[1] = self.getOption('max')

        if rng[0] > rng[1]:
            self.debug("Minimum range greater than maximum: {} > {}, the range/min/max settings are being ignored.", *rng)
            rng = list(self.getRange(local=self.getOption('local_lim')))

        self._vtkmapper.SetScalarRange(rng)
        """

    def getRange(self, local=False):
        """
        Return range of the active variable and blocks.
        """
        #self.__reader.Update()
        #$for reader in self._inputs:
        #    reader.Update()

        if not local:
            return self.__getRange()
        else:
            return self.__getLocalRange()

    def __getRange(self):
        """
        Private version of range for the update method.
        """
        component = self.getOption('component')
        self._vtkmapper.Update()
        data = self._vtkmapper.GetInput()
        out = self.__getActiveArray(data)
        return out.GetRange(component)




        """
        pairs = []

        filter_obj = self._filters['extract']

        #filter_obj.Update() # required to get correct ranges from ExtractBlockFilter
        data = self.GetOutputDataObject(0)
        for i in range(data.GetNumberOfBlocks()):
            current = data.GetBlock(i)
            if isinstance(current, vtk.vtkUnstructuredGrid):
                array = self.__getActiveArray(current)
                if array:
                    pairs.append(array.GetRange(component))

            elif isinstance(current, vtk.vtkMultiBlockDataSet):
                for j in range(current.GetNumberOfBlocks()):
                    array = self.__getActiveArray(current.GetBlock(j))
                    if array:
                        pairs.append(array.GetRange(component))

        return utils.get_min_max(*pairs)
        """
    def __getLocalRange(self):
        """
        Determine the range of visible items.
        """
        component = self.getOption('component')
        #self._vtkmapper.Update()
        data = self._vtkmapper.GetInput()
        out = self.__getActiveArray(data)
        return out.GetRange(component)

    def __getActiveArray(self, data):
        """
        Return the vtkArray for the current variable.

        Inputs:
            data[vtkUnstructuredGrid]: The VTK data object to extract array from.

        see __GetRange and __GetBounds
        """

        name = self.__current_variable.name
        if self.__current_variable.object_type == ExodusReader.ELEMENTAL:
            for a in range(data.GetCellData().GetNumberOfArrays()):
                if data.GetCellData().GetArrayName(a) == name:
                    return data.GetCellData().GetAbstractArray(a)

        elif self.__current_variable.object_type == ExodusReader.NODAL:
            for a in range(data.GetPointData().GetNumberOfArrays()):
                if data.GetPointData().GetArrayName(a) == name:
                    return data.GetPointData().GetAbstractArray(a)
        else:
            self.error('Unable to get the range for the variable "{}"', self.__current_variable.name)

    def _updateOpacity(self, window, binding): #pylint: disable=unuysed-argument
        opacity = self.getOption('opacity')
        if binding.shift:
            if opacity > 0.05:
                opacity -= 0.05
        else:
            if opacity <= 0.95:
                opacity += 0.05
        self.update(opacity=opacity)
        self.printOption('opacity')

    def _updateColorMap(self, window, binding): #pylint: disable=unused-argument
        step = 1 if not binding.shift else -1
        available = self._sources[0]._colormap.names() #pylint: disable=protected-access
        index = available.index(self.getOption('cmap'))

        n = len(available)
        index += step
        if index == n:
            index = 0
        elif index < 0:
            index = n - 1

        self.setOption('cmap', available[index])
        self.printOption('cmap')

    def _updateTimestep(self, window, binding): #pylint: disable=unused-argument
        step = 1 if not binding.shift else -1
        current = self._reader.getTimeData().timestep + step
        n = len(self._reader.getTimes())
        if current == n:
            current = 0
        self._reader.setOption('time', None)
        self._reader.setOption('timestep', current)
        self._reader.printOption('timestep')
