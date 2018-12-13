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
from ExodusReader import ExodusReader
from MultiAppExodusReader import MultiAppExodusReader
import mooseutils
from .. import base
from .. import utils
from .. import filters

@base.addFilter('geometry', filters.GeometryFilter, required=True)
@base.addFilter('extract', filters.ExtractBlockFilter, required=True)
class ExodusResult(base.ChiggerResult):
    """
    Result object to displaying ExodusII data from a single reader.
    """
    VTKACTORTYPE = vtk.vtkActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper
    INPUTTYPE = 'vtkMultiBlockDataSet'

    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()

        # Variable selection
        opt.add('variable', vtype=str, doc="The nodal or elemental variable to render.")
        opt.add('component', -1, vtype=int, allow=(-1, 0, 1, 2),
                doc="The vector variable component to render (-1 plots the magnitude).")

        # Data range
        opt.add('range', vtype=float, size=2,
                doc="The range of data to display on the volume and colorbar; range takes " \
                    "precedence of min/max.")
        opt.add('local_range', False, "Use local range when computing the default data range.")
        opt.add('min', vtype=float, doc="The minimum range.")
        opt.add('max', vtype=float, doc="The maximum range.")

        # Subdomains/sidesets/nodesets
        opt.add('nodeset', None, vtype=list,
                doc="A list of nodeset ids or names to display, use [] to display all nodesets.")
        opt.add('boundary', None, vtype=list,
                doc="A list of boundary ids (sideset) ids or names to display, use [] to display " \
                    "all sidesets.")
        opt.add('block', [], vtype=list,
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

        bindings = base.ChiggerResult.validKeyBindings()

        # Opacity keybindings
        bindings.add('a', ExodusResult._updateOpacity,
                     desc='Increase the alpha (opacity) by 1%.')
        bindings.add('a', ExodusResult._updateOpacity, shift=True,
                     desc='Decrease the alpha (opacity) by 1%.')

        # Colormap keybindings
        bindings.add('m', ExodusResult._updateColorMap,
                     desc="Toggle through available colormaps.")
        bindings.add('m', ExodusResult._updateColorMap, shift=True,
                     desc="Toggle through available colormaps, in reverse direction.")

        # Time keybindngs
        bindings.add('t', ExodusResult._updateTimestep,
                     desc="Increase timestep by 1.")
        bindings.add('t', ExodusResult._updateTimestep, shift=True,
                     desc="Decrease the timestep by 1.")

        return bindings

    def applyOptions(self):

        for vtkmapper in self._vtkmappers:
            vtkmapper.SelectColorArray('u')
            vtkmapper.SetScalarModeToUsePointFieldData()
            vtkmapper.InterpolateScalarsBeforeMappingOn()


        block_info = self._inputs[0].getBlockInformation()
        print block_info
        for item in ['block', 'boundary', 'nodeset']:
            opt = self.getOption(item)
            if opt == []:
                self.setOption(item, [item.name for item in \
                                      block_info[getattr(ExodusReader, item.upper())].itervalues()])


    #def __init__(self, reader, **kwargs):
    #    base.ChiggerResult(reader, **kwargs)

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
    #    #super(ExodusResult, self).__init__(*sources, **kwargs)

    #    self.__outline_result = None

    """
    def update(self, **kwargs):
        super(ExodusResult, self).update(**kwargs)

        # Update the ExodusReader objects
        self._reader.update()

        # Do not mess with the range if there is a source without a variable
        if any([src.getCurrentVariableInformation() is None for src in self._sources]):
            return

        # Re-compute ranges for all sources
        rng = list(self.getRange(local=self.getOption('local_range')))
        if self.isOptionValid('range'):
            rng = self.getOption('range')
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
