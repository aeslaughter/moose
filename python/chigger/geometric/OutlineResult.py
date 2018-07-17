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
from . import OutlineSource, OutlineSource2D

#from OutlineSource import OutlineSource

class OutlineResult(base.ChiggerResult):

    @staticmethod
    def validOptions():
        opt = base.ChiggerResult.validOptions()
        opt += OutlineSource.validOptions()
        return opt

    def __init__(self, result, **kwargs):
        sources = []
        for src in result.getSources():
            if isinstance(src.getVTKActor(), vtk.vtkActor2D):
                sources.append(OutlineSource2D(src))
            else:
                sources.append(OutlineSource(src))
        super(OutlineResult, self).__init__(*sources, renderer=result.getVTKRenderer(), **kwargs)

    """
    def addSource(self, source):
        super(OutlineResult, self).addSource(source)
        super(OutlineResult, self).addSource(OutlineSource(source))

    def removeSource(self, source):
        super(OutlineResult, self).removeSource(source)

        for source in self._sources:
            if isinstance(source,
    """
