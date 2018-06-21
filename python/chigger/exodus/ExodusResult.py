#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from ExodusSource import ExodusSource
from ExodusReader import ExodusReader
from MultiAppExodusReader import MultiAppExodusReader
import mooseutils
from .. import base
from .. import utils
from .. import geometric

class ExodusResult(base.ChiggerResult):
    """
    Result object to displaying ExodusII data from a single reader.
    """
    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()
        opt += ExodusSource.validOptions()
        opt.add('explode', None, "When multiple sources are being used (e.g., NemesisReader) "
                                 "setting this to a value will cause the various sources to be "
                                 "'exploded' away from the center of the entire object.",
                vtype=float)

        return opt

    def __init__(self, reader, **kwargs):

        self._reader = reader

        # Build the ExodusSource objects
        #TODO: Create an ExodusReaderResult object to allow other items to use the reader, for automatic time updating stuff...
        if isinstance(reader, ExodusReader):
            sources = [ExodusSource(reader)]
        elif isinstance(reader, MultiAppExodusReader):
            sources = [ExodusSource(r) for r in reader]
        else:
            raise mooseutils.MooseException('The supplied object of type {} is not supported, '
                                            'only ExodusReader and MultiAppExodusReader objects '
                                            'may be utilized.'.format(reader.__class__.__name__))

        # Supply the sources to the base class
        super(ExodusResult, self).__init__(*sources, **kwargs)

        # Opacity keybindings
        self.addKeyBinding('o', self._updateOpacity, desc='Decrease the opacity by 1%')
        self.addKeyBinding('o', self._updateOpacity, shift=True,
                           desc='Decrease the opacity by 1%')

        # Colormap keybindings
        self.addKeyBinding('m', self._updateColorMap, desc="Toggle through available colormaps.")
        self.addKeyBinding('m', self._updateColorMap, shift=True,
                           desc="Toggle through available colormaps, in reverse direction.")

        # Time keybindngs
        self.addKeyBinding('t', self._updateTimestep, desc="Increase timestep by 1.")
        self.addKeyBinding('t', self._updateTimestep, shift=True, desc="Decrease the timestep by 1.")

        self.__outline_result = None

    def update(self, **kwargs):
        super(ExodusResult, self).update(**kwargs)

        # Do not mess with the range if there is a source without a variable
        if any([src.getCurrentVariableInformation() is None for src in self._sources]):
            return

        # Re-compute ranges for all sources
        rng = list(self.getRange()) # Use range from all sources as the default
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
            factor = self.getOption('explode')
            m = self.getCenter()
            for src in self._sources:
                c = src.getVTKActor().GetCenter()
                d = (c[0]-m[0], c[1]-m[1], c[2]-m[2])
                src.getVTKActor().AddPosition(d[0]*factor, d[1]*factor, d[2]*factor)

    def getRange(self):
        """
        Return the min/max range for the selected variables and blocks/boundary/nodeset.

        NOTE: For the range to be restricted by block/boundary/nodest the reader must have
              "squeeze=True", which can be much slower.
        """
        #self.checkUpdateState()
        rngs = [src.getRange() for src in self._sources]
        return utils.get_min_max(*rngs)

    def getCenter(self):
        """
        Return the center (based on the bounds) of all the objects.
        """
        a, b = self.getBounds()
        return ((b[0]-a[0])/2., (b[1]-a[1])/2., (b[2]-a[2])/2.)

    def _updateOpacity(self, window, binding):
        opacity = self.getOption('opacity')
        if binding.shift:
            if opacity > 0.05:
                opacity -= 0.05
        else:
            if opacity <= 0.95:
                opacity += 0.05
        self.update(opacity=opacity)

    def _updateColorMap(self, window, binding):
        step = 1 if not binding.shift else -1
        available = self._sources[0]._colormap.names()
        index = available.index(self.getOption('cmap'))

        n = len(available)
        index += step
        if index == n:
            index = 0
        elif index < 0:
            index = n - 1

        self.setOption('cmap', available[index])
        self.printOption('cmap')

    def _updateTimestep(self, window, binding):
        step = 1 if not binding.shift else -1
        current = self._reader.getTimeData().timestep + step
        n = len(self._reader.getTimes())
        if current == n:
            current = 0
        self._reader.setOption('time', None)
        self._reader.setOption('timestep', current)
        self._reader.printOption('timestep')
