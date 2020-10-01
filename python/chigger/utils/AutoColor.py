#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
from .Option import Option

class Color(object):
    """A Class to handle RGB color values"""

    def __init__(self, *args):
        self.__option = Option('__Color__', vtype=(int, float), size=3,
                               verify=(self.__verify, "The supplied RGB color values must be in range [0,1]"))

        if args:
            self.__option.value = args

    def rgb(self):
        """Return the RGB values"""
        return self.__option.value

    def __verify(self, values):
        """Verify that the supplied values are in the correct range"""
        return all([v >= 0 and v <= 1 for v in values])

class AutoColor(Color):
    """A Class to handle RGB color values that operate with background color automatically."""


def auto_adjust_color(parent, children):
    """
    Helper function for automatically adjusting colors for the background.

    Inputs:
        parent[Window|Viewport]: Object with background settings
        children[ChiggerSourceBase]: Source objects with color settings

    see Window.py Viewport.py
    """
    if parent.isOptionValid('background', 'color') and (not parent.isOptionValid('background', 'color2')):
        bg = parent.getOption('background', 'color')
        color = Color(1., 1., 1.) if sum(bg.rgb()) < 1.5 else Color(0., 0., 0.)
        for child in children:
            for param in child._options.parameters():
                if param.vtype and (AutoColor in param.vtype) and (param.value is None):
                    param.value = color
