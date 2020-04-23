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
import mooseutils

from .ExodusReader import ExodusReader
from .MultiAppExodusReader import MultiAppExodusReader
from .. import base
from .. import utils
from .. import filters

class ExodusSource(base.ChiggerSource):
    """
    Source object to displaying ExodusII data from a reader. The reader and source objects are
    separate to allow for one reader to be used with many sources, which is more efficient.

    Inputs:
        viewport[chigger.Viewport]: The viewport object that the source should be rendered.
        reader[chigger.exodus.ExodusReader]: The reader object containing the data to be rendered.
        kwargs: Key-value pair options.
    """
    VTKACTORTYPE = vtk.vtkActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper

    @staticmethod
    def validParams():
        opt = base.ChiggerSource.validParams()

        # Variable selection
        opt.add('variable', vtype=str, doc="The nodal or elemental variable to render.")
        opt.add('component', -1, vtype=int, allow=(-1, 0, 1, 2),
                doc="The vector variable component to render (-1 plots the magnitude).")

        # Data range
        opt.add('lim', vtype=float, size=2,
                doc="The range of data to display on the volume and colorbar; range takes " \
                    "precedence of min/max.")
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

        # Colormap
        opt.add('cmap', base.ColorMap.validParams())

        opt.add('explode', None, vtype=float,
                doc="When multiple sources are being used (e.g., NemesisReader) setting this to a "
                    "value will cause the various sources to be 'exploded' away from the center of "
                    "the entire object.")
        return opt

    @staticmethod
    def validKeyBindings():

        bindings = base.ChiggerSource.validKeyBindings()

        """

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
        """
        return bindings

    def __init__(self, viewport, reader, **kwargs):

        self.__reader = reader
        self.__current_variable = None
        self._colormap = base.ColorMap()

        base.ChiggerSource.__init__(self, viewport,
                                    nInputPorts=1, inputType='vtkMultiBlockDataSet',
                                    nOutputPorts=1, outputType='vtkMultiBlockDataSet',
                                    **kwargs)

        self._addAlgorithm(self.__reader)
        self.SetInputConnection(self.__reader.GetOutputPort())

        self._addFilter(filters.ExtractBlockFilter, True)
        self._addFilter(filters.GeometryFilter, True)

        # TODO: Check 'blocks', etc. and warn if set
        # TODO: Check 'variables' set

    #def updateModified(self):
    #    """
    #    """
    #    self.__reader.updateModified()
    #    base.ChiggerSource.updateModified(self)


    def _onRequestInformation(self, inInfo, outInfo):
        base.ChiggerSource._onRequestInformation(self, inInfo, outInfo)

        # Colormap
        if not self.getParam('color'):
            self._colormap.parameters().update(self.getParam('cmap'))
            self._vtkmapper.SetLookupTable(self._colormap())

        # Update the block/boundary/nodeset and variable settings on the reader
        self.__updateActiveBlocks()
        self.__updateActiveVariables()
        self.__reader.updateInformation() # the above apply settings to the reader

        # Update the block/boundary/nodeset settings to convert [] to all.
        extract_indices = []
        block_info = self.__reader.getBlockInformation()
        for binfo in block_info.values():
            for b in binfo:
                if b.active:
                    extract_indices.append(b.multiblock_index)

        fobject = self._filters['extract']
        fobject.setParam('indices', extract_indices)

        # Misc. mapper settings
        self._vtkmapper.InterpolateScalarsBeforeMappingOn()
        self._vtkmapper.UseLookupTableScalarRangeOff()

    def _onRequestData(self, inInfo, outInfo):
        """(protected, override)
        Passes the reader data to the output port to allow for filters to be applied and
        updates the range of the vtkMapper based on the available data or the user supplied options.
        """
        base.ChiggerSource._onRequestData(self, inInfo, outInfo)
        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt.ShallowCopy(inp)

        self.__setDataRange(opt)

    def __setDataRange(self, out_data):
        """(private)
        Computes the range from the data and applies the user specified range settings.
        """

        rng = self.__getDataRange(out_data)
        if self.isParamValid('lim'):
            rng = self.getParam('lim')
        else:
            if self.isParamValid('min'):
                rng[0] = self.getParam('min')
            if self.isParamValid('max'):
                rng[1] = self.getParam('max')

        if rng[0] > rng[1]:
            self.debug("Minimum range greater than maximum: {} > {}, the range/min/max settings are being ignored.", *rng)
            rng = self.__getDataRange(out_data)

        self._vtkmapper.SetScalarRange(rng)

    def __getDataRange(self, out_data):
        """(private)
        Return the range of all active blocks for the current variable and component.
        """

        variable = self.getParam('variable')
        component = self.getParam('component')
        rng = [float('inf'), -float('inf')]
        for i in range(out_data.GetNumberOfBlocks()):
            for j in range(out_data.GetBlock(i).GetNumberOfBlocks()):
                data = out_data.GetBlock(i).GetBlock(j)
                if data:
                    pdata = out_data.GetBlock(i).GetBlock(j).GetPointData()
                    for k in range(pdata.GetNumberOfArrays()):
                        array = pdata.GetAbstractArray(k)
                        if array.GetName() == variable:
                            local = [0, 0]
                            array.GetRange(local, component)
                            rng = [min(rng[0], local[0]), max(rng[1], local[1])]
                    cdata = out_data.GetBlock(i).GetBlock(j).GetCellData()
                    for k in range(cdata.GetNumberOfArrays()):
                        array = cdata.GetAbstractArray(k)
                        if array.GetName() == variable:
                            local = [0, 0]
                            array.GetRange(local, component)
                            rng = [min(rng[0], local[0]), max(rng[1], local[1])]
        return rng

    def __updateActiveBlocks(self):
        self.debug('__updateActiveBlocks')

        block_info = self.__reader.getBlockInformation()
        self.__setActiveBlocksHelper('blocks', block_info[ExodusReader.BLOCK])
        self.__setActiveBlocksHelper('sidesets', block_info[ExodusReader.SIDESET])
        self.__setActiveBlocksHelper('nodesets', block_info[ExodusReader.NODESET])

    def __updateActiveVariables(self):
        self.debug('__updateActiveVariables')

        vname = self.getParam('variable')
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
            current = self.__reader.getParam('variables')
            current = current + (vfullname,) if current is not None else (vfullname,)
            self.__reader.setParam('variables', current)
            self._vtkmapper.SelectColorArray(vname)

        # Component
        component = -1 # Default component to utilize if not valid
        if self.isParamValid('component'):
            component = self.getParam('component')

        if component == -1:
            self._vtkmapper.GetLookupTable().SetVectorModeToMagnitude()
        else:
            if component > varinfo.num_components:
                msg = 'Invalid component number ({}), the variable "{}" has {} components.'
                mooseutils.mooseError(msg.format(component, varinfo.name, varinfo.num_components))
            self._vtkmapper.GetLookupTable().SetVectorModeToComponent()
            self._vtkmapper.GetLookupTable().SetVectorComponent(component)

    def __setActiveBlocksHelper(self, param, binfo):

        local = self.getParam(param)
        if local == []:
            local = tuple([b.name for b in binfo])

        if local is not None:
            self.__reader.setParam(param, self.__reader.getParam(param) + local)

    """
        # Explode
        if self.isParamValid('explode'):
            factor = self.applyOption('explode')
            m = self.getCenter()
            for src in self._sources:
                c = src.getVTKActor().GetCenter()
                d = (c[0]-m[0], c[1]-m[1], c[2]-m[2])
                src.getVTKActor().AddPosition(d[0]*factor, d[1]*factor, d[2]*factor)
    """

    """
    def _updateOpacity(self, window, binding): #pylint: disable=unuysed-argument
        opacity = self.getParam('opacity')
        if binding.shift:
            if opacity > 0.05:
                opacity -= 0.05
        else:
            if opacity <= 0.95:
                opacity += 0.05
        self.update(opacity=opacity)
        self.printParam('opacity')

    def _updateColorMap(self, window, binding): #pylint: disable=unused-argument
        step = 1 if not binding.shift else -1
        available = self._sources[0]._colormap.names() #pylint: disable=protected-access
        index = available.index(self.getParam('cmap'))

        n = len(available)
        index += step
        if index == n:
            index = 0
        elif index < 0:
            index = n - 1

        self.setParam('cmap', available[index])
        self.printParam('cmap')

    def _updateTimestep(self, window, binding): #pylint: disable=unused-argument
        step = 1 if not binding.shift else -1
        current = self._reader.getTimeData().timestep + step
        n = len(self._reader.getTimes())
        if current == n:
            current = 0
        self._reader.setParam('time', None)
        self._reader.setParam('timestep', current)
        self._reader.printParam('timestep')
    """
