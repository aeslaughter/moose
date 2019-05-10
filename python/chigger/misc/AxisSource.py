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
from .. import base
from .. import utils
from ..Window import Window

#@Window.addBackgroundOptions('color')
class AxisSource(base.ChiggerSource):
    """
    Creates an Axis with limits, ticks, etc.
    """

    VTKACTORTYPE = vtk.vtkAxisActor2D#vtk.vtkContextActor
    VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D#None

    __TEXTKEYS__ = utils.TextOptions.validOptions().keys()

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()

        # Axis Line Options
        opt += utils.ActorOptions.validOptions()
        opt.setDefault('linewidth', 2)

        # Title and label Options
        # This object includes general properties ('fontcolor', 'fontopacity', ...) as well as
        # title and label specific properties ('title_fontcolor', ..., 'label_fontcolor'). The
        # default 'fontcolor' and 'fontopacity' are removed to allow the the 'color' and 'opacity'
        # to be the default for this options
        opt.add('title', vtype=str, doc="The title for the axis.")
        opt += utils.TextOptions.validOptions()
        opt += utils.TextOptions.validOptions(prefix='title', unset=True)
        opt += utils.TextOptions.validOptions(prefix='label', unset=True)
        opt.set('fontcolor', None)
        opt.set('fontopacity', None)
        opt.set('fontitalic', False)

        # Position
        opt.add('point1', vtype=float, size=2, doc="The starting position, in relative viewport coordinates, of the axis line.")
        opt.add('point2', vtype=float, size=2, doc="The ending position, in relative viewport coordinates, of the axis line.")

        return opt

    def __init__(self, **kwargs):
        base.ChiggerSource.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)

    def applyOptions(self):
        """
        Update the vtkAxis with given settings. (override)

        Inputs:
            see ChiggerFilterSourceBase
        """
        base.ChiggerSource.applyOptions(self)
        utils.ActorOptions.applyOptions(self._vtkactor, self._options)

        self._vtkactor.SetPoint1(*self.getOption('point1'))
        self._vtkactor.SetPoint2(*self.getOption('point2'))
        self.setOption('title', self._vtkactor.SetTitle)

        # The default font color and opacity should match the 'color' and 'opactity' options
        if not self.isOptionValid('fontcolor'):
            self._options.set('fontcolor', self.getOption('color'))

        if not self.isOptionValid('fontopacity'):
            self._options.set('fontopacity', self.getOption('opacity'))

        # Set the values of the title_
        for name in self.__TEXTKEYS__:
            for subname in ['title', 'label']:
                tname = '{}_{}'.format(subname, name)
                if not self.isOptionValid(tname):
                    self._options.set(tname, self._options.get(name))

        utils.TextOptions.applyOptions(self._vtkactor.GetTitleTextProperty(), self._options, 'title')
        utils.TextOptions.applyOptions(self._vtkactor.GetLabelTextProperty(), self._options, 'label')
