#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from ChiggerObject import ChiggerObject
from ChiggerAlgorithm import ChiggerAlgorithm
from ChiggerSource import ChiggerSource
from ChiggerCompositeSource import ChiggerCompositeSource

# "utils" would be the correct place for this, but it creates a cyclic dependency because it used
# base ChiggerObject; "misc" has a similar problem and "misc" is reserved for source objects
from ColorMap import ColorMap

def addFilter(filtertype, required=False):
    """Decorator for adding filters."""
    def create(cls):
        cls.__FILTERS__.append(filtertype)
        if required:
            cls.__ACTIVE_FILTERS__.add(filtertype.FILTERNAME)
        return cls
    return create


def backgroundOptions(*args):
    """Decorator for adding automatic color settings for black/white background"""
    def create(cls):
        cls.__BACKGROUND_OPTIONS__.update(args)
        return cls
    return create
