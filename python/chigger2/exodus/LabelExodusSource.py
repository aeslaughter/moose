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
from ExodusSource import ExodusSource
from ExodusReader import ExodusReader
import mooseutils
from .. import base
from .. import filters
from .. import utils

class LabelExodusSource(base.ChiggerSource2D):
    """
    Object for attaching labels to an ExodusSource object.

    Args:
        result[ExodusSource]: The ExodusSource object to label.
    """
    FILTER_TYPES = [filters.IdFilter, filters.CellCenters, filters.SelectVisiblePoints]

    @staticmethod
    def validParams():
        opt = base.ChiggerSource2D().validParams()
        opt += utils.FontOptions.validParams()
        opt.add('label_type', default='variable', vtype=str,
                doc="Specify the type of label to create.",
                allow=('point', 'cell', 'variable'))
        opt.set('justification', 'center')
        opt.set('vertical_justification', 'middle')
        return opt

    def __init__(self, exodus_source, **kwargs):
        super(LabelExodusSource, self).__init__(vtkmapper_type=vtk.vtkLabeledDataMapper, **kwargs)

        if not isinstance(exodus_source, ExodusSource):
            msg = 'The supplied object of type {} must be a ExodusSource object.'
            raise mooseutils.MooseException(msg.format(exodus_source.__class__.__name__))

        self._exodus_source = exodus_source

    def getVTKSource(self):
        """
        Returns the vtkExtractBlock object used for pulling subdomsin/sideset/nodeset data from the
        reader. (override)

        Returns:
            vtk.vtkExtractBlock (see ChiggerFilterSourceBase)
        """
        return self._exodus_source.getFilters()[-1].getVTKFilter()

    def update(self, **kwargs):
        """
        Update the settings for this object.
        """

        # Apply options (update can't be called here b/c the required filters need to be set first)
        self.setParams(**kwargs)

        # Update the required filters based on the label type.
        label_type = self.getParam('label_type')
        if label_type == 'cell':
            self._required_filters = [filters.IdFilter(), filters.CellCenters(),
                                      filters.SelectVisiblePoints()]
            self._vtkmapper.SetLabelModeToLabelIds()
        elif label_type == 'point':
            self._required_filters = [filters.IdFilter(), filters.SelectVisiblePoints()]
            self._vtkmapper.SetLabelModeToLabelIds()
        else:
            varinfo = self._exodus_source.getCurrentVariableInformation()
            if varinfo.object_type == ExodusReader.ELEMENTAL:
                self._required_filters = [filters.CellCenters(), filters.SelectVisiblePoints()]
            else:
                self._required_filters = [filters.SelectVisiblePoints()]
            self._vtkmapper.SetFieldDataName(self._exodus_source.getParam('variable'))
            self._vtkmapper.SetLabelModeToLabelFieldData()

        # Call base class to connect filters/mappers
        super(LabelExodusSource, self).update()

        # Set the renderer for the SelectVisiblePoints filter
        self._required_filters[-1].getVTKFilter().SetRenderer(self._vtkrenderer)

        # Update fonts
        utils.FontOptions.applyOptions(self._vtkmapper.GetLabelTextProperty(), self._options)
