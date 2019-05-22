#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import copy
import logging
import vtk
from .. import base
from .. import utils

@base.backgroundOptions('color')
class Axis2D(base.ChiggerSource):
    """
    Creates an Axis with limits, ticks, etc.
    """

    VTKACTORTYPE = vtk.vtkAxisActor2D#vtk.vtkContextActor
    #VTKMAPPERTYPE = vtk.vtkPolyDataMapper2D#None

    __TEXTKEYS__ = utils.TextOptions.validOptions().keys()

    @staticmethod
    def validOptions():
        opt = base.ChiggerSource.validOptions()

        # Axis Line Options
        opt += utils.ActorOptions.validOptions()
        opt.set('linewidth', 1)

        # Title and label Options
        # This object includes general properties ('fontcolor', 'fontopacity', ...) as well as
        # title and label specific properties ('title_fontcolor', ..., 'label_fontcolor'). The
        # default 'fontcolor' and 'fontopacity' are removed to allow the the 'color' and 'opacity'
        # to be the default for this options
        opt.add('title', vtype=str, doc="The title for the axis.")
        opt.add('title_position', 0.5, vtype=float,
                doc="Set the title position between 0 (start) and 1 (end).")
        opt.append(utils.TextOptions.validOptions(), exclude=['opacity', 'color'])
        opt.append(utils.TextOptions.validOptions(), prefix='title_', unset=True)
        opt.append(utils.TextOptions.validOptions(), prefix='label_', unset=True)

        #opt += utils.TextOptions.validOptions(prefix='title', unset=True)
        #opt += utils.TextOptions.validOptions(prefix='label', unset=True)
        #opt.set('fontcolor', None)
        #opt.set('fontopacity', None)
        #opt.set('fontitalic', False)

        # Position
        opt.add('point1', vtype=float, size=2, doc="The starting position, in relative viewport coordinates, of the axis line.")
        opt.add('point2', vtype=float, size=2, doc="The ending position, in relative viewport coordinates, of the axis line.")

        # Range
        opt.add('range', (0, 1), vtype=float, size=2, doc="The axis numeric range.")
        opt.add('adjust_range', False, vtype=bool, doc="Adjust the range to 'nice' values.")

        # Major ticks
        opt.add('major_nticks', vtype=int, doc="The number of tick marks.")
        opt.add('major_offset', vtype=int, doc="Offset between tick mark and label.")
        opt.add('major_length', 16, vtype=int, doc="Length of the tick marks.")

        # Minor ticks
        opt.add('minor_nticks', vtype=int, doc="The number of tick marks.")
        opt.add('minor_length', 8, vtype=int, doc="Length of the tick marks.")

        # Axis
        opt.add('axis', True, vtype=bool, doc="Show/hide the axis line.")
        opt.add('format', vtype=str, doc="Label format in printf form.")

        return opt

    def __init__(self, **kwargs):
        base.ChiggerSource.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)
        #self._vtkactor.UseFontSizeFromPropertyOn()



    def applyOptions(self):
        """
        Update the vtkAxis with given settings. (override)

        Inputs:
            see ChiggerFilterSourceBase
        """
        base.ChiggerSource.applyOptions(self)
        utils.ActorOptions.applyOptions(self._vtkactor, self._options)

        # Location
        self._vtkactor.SetPoint1(*self.getOption('point1'))
        self._vtkactor.SetPoint2(*self.getOption('point2'))

        # Title
        if self.isOptionValid('title'):
            self._vtkactor.SetTitleVisibility(True)
            self._vtkactor.SetTitle(self.getOption('title'))
        else:
            self._vtkactor.SetTitleVisibility(False)
        self.assignOption('title_position', self._vtkactor.SetTitlePosition)

        # The default font color and opacity should match the 'color' and 'opactity' options
        #if not self.isOptionValid('fontcolor'):
        #    self._options.set('fontcolor', self.getOption('color'))

        #if not self.isOptionValid('fontopacity'):
        #    self._options.set('fontopacity', self.getOption('opacity'))

        # Set the values of the title_
        for name in self.__TEXTKEYS__:
            for subname in ['title', 'label']:
                tname = '{}_{}'.format(subname, name)
                if not self.isOptionValid(tname):
                    self._options.set(tname, self._options.get(name))

        utils.TextOptions.applyOptions(self._vtkactor.GetTitleTextProperty(), self._options, 'title')
        utils.TextOptions.applyOptions(self._vtkactor.GetLabelTextProperty(), self._options, 'label')

        # Range
        self.assignOption('range', self._vtkactor.SetRange)
        self.assignOption('adjust_range', self._vtkactor.SetAdjustLabels)

        # Major tick marks
        num = self.getOption('major_nticks')
        if (num is not None) and self.getOption('adjust_range'):
            self.log("The 'major_number' option is not applied if 'adjust_range' is enabled.", level=logging.WARNING)
        if num is not None:
            if (num > 0):
                self._vtkactor.SetNumberOfLabels(num)
                self._vtkactor.SetTickVisibility(True)
            else:
                self._vtkactor.SetTickVisibility(False)

        self.assignOption('major_length', self._vtkactor.SetTickLength)
        self.assignOption('major_offset', self._vtkactor.SetTickOffset)

        # Minor tick marks
        self.assignOption('minor_nticks', self._vtkactor.SetNumberOfMinorTicks)
        self.assignOption('minor_length', self._vtkactor.SetMinorTickLength)

        # Axis Line
        self.assignOption('axis', self._vtkactor.SetAxisVisibility)
        self.assignOption('format', self._vtkactor.SetLabelFormat)
