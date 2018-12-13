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

from ChiggerSourceBase import ChiggerSourceBase
from ChiggerFilterSourceBase import ChiggerFilterSourceBase
from ChiggerSource import ChiggerSource
from ChiggerSource2D import ChiggerSource2D

from ChiggerResultBase import ChiggerResultBase
from ChiggerResult import ChiggerResult

from ColorMap import ColorMap

from ResultGroup import ResultGroup

def create_single_source_result(source_type):
    """
    In many cases only a single source object (ChiggerSourceBase) must be linked to a renderer
    (ChiggerResult), as is the case for the annotations (e.g., TextAnnotation). To avoid creating
    nearly identical classes for each these cases this function can be used to generate the class
    needed based on the type provided.

    Inputs:
        source_type: The type of source to attach to a ChiggerResult object.
    """
    class ChiggerResultMeta(ChiggerResult):
        """
        Meta class for creating ChiggerResult classes of different types.
        """
        @staticmethod
        def validOptions():
            opt = ChiggerResult.validOptions()
            opt += source_type.validOptions()
            return opt

        def __init__(self, **kwargs):
            super(ChiggerResultMeta, self).__init__(source_type(), **kwargs)

        #def update(self, **kwargs):
        #    super(ChiggerResultMeta, self).update(**kwargs)

    return ChiggerResultMeta


def addFilter(filtertype, required=False):
    """Decorator for adding filters."""
    def create(cls):
        cls.__FILTERS__.append(filtertype)
        if required:
            cls.__ACTIVE_FILTERS__.add(filtertype.FILTERNAME)
        return cls
    return create
