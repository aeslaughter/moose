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
from .. import utils
from .. import base

class TextAnnotationSource(base.ChiggerSourceBase):
    """
    Source for creating text annotations.
    """

    @staticmethod
    def validOptions():
        """
        Return default options for this object.
        """
        opt = base.ChiggerSourceBase.validOptions()
        #opt.add('position', (0.5, 0.5), "The text position within the viewport, in relative "
        #                                "coordinates.", vtype=float)
        opt.add('text', None, "The text to display.", vtype=str)
        #opt += utils.FontOptions.validOptions()
        return opt

    def __init__(self, **kwargs):
        super(TextAnnotationSource, self).__init__(vtkactor_type=vtk.vtkActor2D,
                                                   vtkmapper_type=vtk.vtkTextMapper, **kwargs)
        self._vtkactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()

    def update(self, **kwargs):
        """
        Updates the settings for the text creation. (override)
        """
        super(TextAnnotationSource, self).update(**kwargs)

        #utils.FontOptions.applyOptions(self._vtkmapper.GetTextProperty(), self._options)

        #if self.isOptionValid('position'):
        #    self._vtkactor.GetPositionCoordinate().SetValue(*self.applyOption('position'))

        if self.isOptionValid('text'):
        #    self._vtkmapper.GetTextProperty().Modified()
            self._vtkmapper.SetInput(self.applyOption('text'))
        #    print 'Setting text:', self.applyOption('text')

        # if options applied ... perform render
        #self._vtkrenderer.GetRenderWindow().Render()
