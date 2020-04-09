#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import numpy as np
import vtk
from .. import base, geometric, utils

class ColorBar(base.ChiggerCompositeSource):
    """
    A generic colorbar, that can be rotated and contain dual axis.

    The default colorbar in VTK, vtkScalarBarActor, tightly couples the tick marks with the bar
    width, which makes it difficult to control either. This class decouples the colorbar and labels.
    """
    @staticmethod
    def validOptions():
        opt = base.ChiggerCompositeSource.validOptions()
        opt.add('origin', (0.5, 0.5), vtype=float, size=2, doc="Define the center of the colorbar, in relative viewport coordinates.")
        opt.add('width', 0.025, vtype=float, doc="The width of the colorbar, in relative viewport coordinates.")
        opt.add('length', 0.7, vtype=float, doc="The length of the colorbar, in relative viewport coordinates.")
        opt.add('cmap', 'cividis', vtype=str, doc="The color map name.")
        opt.add('reverse', False, vtype=bool, doc="Reverse the color map.")
        opt.add('resolution', 256, vtype=int, doc="The number of colors and polygons to use when creating colorbar geometry.")
        opt.add('rotate', 0, vtype=int, doc="Counter clock-wise rotation of color bar; use 90 to create a horizontal bar.")
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = base.ChiggerCompositeSource.validKeyBindings()

        #bindings.add('w', lambda s, *args: ColorBar._increment(s, 0.005, 'width', *args),
        #             desc="Increase the width of the colorbar by 0.005.")
        #bindings.add('w', lambda s, *args: ColorBar._increment(s, -0.005, 'width', *args),
        #             shift=True,
        #             desc="Decrease the width of the colorbar by 0.005.")
        #bindings.add('l', lambda s, *args: ColorBar._increment(s, 0.005, 'length', *args),
        #             desc="Increase the length of the colorbar by 0.005.")
        #bindings.add('l', lambda s, *args: ColorBar._increment(s, -0.005, 'length', *args),
        #             shift=True, desc="Decrease the length of the colorbar by 0.005.")
        #bindings.add('f', lambda s, *args: ColorBar._incrementFont(s, 1),
        #             desc="Increase the font size by 1 point (when result is selected).")
        #bindings.add('f', lambda s, *args: ColorBar._incrementFont(s, -1), shift=True,
        #             desc="Decrease the font size by 1 point (when result is selected).")
        return bindings

    def __init__(self, *args, **kwargs):
        super(ColorBar, self).__init__(geometric.Rectangle(*args), **kwargs)


    def applyOptions(self):

        # ColorBar Rectangle
        rectangle = self._sources[0]

        origin = self.getOption('origin')
        width = self.getOption('width')
        length = self.getOption('length')
        angle = self.getOption('rotate')

        p0 = (origin[0]-width/2., origin[1]-length/2., 0)
        p1 = (p0[0] + width, p0[1], 0)
        p2 = (p0[0], p0[1] + length, 0)

        res = self.getOption('resolution')
        rectangle.setOptions(origin=p0, point1=p1, point2=p2,
                             cmap=self.getOption('cmap'),
                             cmap_num_colors=res,
                             rotate=self.getOption('rotate'),
                             cmap_reverse=self.getOption('reverse'),
                             resolution=(1, res))

        data = rectangle.getOption('point_data')
        if (data is None) or (data.GetNumberOfTuples() != res):
            rectangle.setOption('point_data', self.__computeColorMapPointData(res))


        base.ChiggerCompositeSource.applyOptions(self)


    @staticmethod
    def __computeColorMapPointData(n):
        m = 1
        data = vtk.vtkFloatArray()
        data.SetName('data')
        data.SetNumberOfTuples((n+1)*(m+1))
        ydata = np.linspace(0, 1, n+1)
        idx = 0
        for i in range(n+1):
            for j in range(m+1):
                data.SetValue(idx, 1-ydata[i])
                idx += 1
        return data

    def onMouseMoveEvent(self, position):
        """
        Update the colorbar origin.
        """
        self.setOption('colorbar_origin', position)
        self.printOption('colorbar_origin')

    def _increment(self, increment, name, *args): #pylint: disable=unused-argument
        """
        Helper for changing the width and length of the colorbar.
        """
        value = self.getOption(name) + increment
        if value < 1 and value > 0:
            self.printOption(name)
            self.setOption(name, value)

    def _incrementFont(self, increment, *args): #pylint: disable=unused-argument
        """
        Helper for changing the font sizes.
        """

        def set_font_size(ax): #pylint: disable=invalid-name
            """Helper for setting both the label and tile fonts."""
            fz_tick = ax.getVTKSource().GetLabelProperties().GetFontSize() + increment
            fz_title = ax.getVTKSource().GetTitleProperties().GetFontSize() + increment
            if fz_tick > 0:
                ax.setOption('tick_font_size', fz_tick)
                ax.printOption('tick_font_size')

            if fz_title > 0:
                ax.setOption('title_font_size', fz_title)
                ax.printOption('title_font_size')

        _, axis0, axis1 = self._sources #pylint: disable=unbalanced-tuple-unpacking
        set_font_size(axis0)
        set_font_size(axis1)
