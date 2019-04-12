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
from ChiggerAlgorithm import ChiggerAlgorithm
from chigger import utils

class ChiggerSource(ChiggerAlgorithm):

    # The type of vtkProp to create (this should be defined in child class)
    VTKACTORTYPE = None

    # The type of vtkAbstractMapper to create (this should be defined in child class)
    VTKMAPPERTYPE = None

    # List of possible filters, this is an internal item. Filters are added with addFilter decorator
    __FILTERS__ = list()

    # List of active filters
    __ACTIVE_FILTERS__ = set()

    @classmethod
    def validOptions(cls):
        opt = ChiggerAlgorithm.validOptions()
        opt += utils.ActorOptions.validOptions()

        for filter_type in cls.__FILTERS__:
            opt.add(filter_type.FILTERNAME,
                    filter_type.validOptions(),
                    doc="Options for the '{}' filter.".format(filter_type.FILTERNAME))

        return opt

    def __init__(self, *args, **kwargs):
        #self.__initialized = False

        # Create mapper
        self._vtkmapper = self.VTKMAPPERTYPE() if self.VTKMAPPERTYPE else None
        if (self._vtkmapper is not None) and not isinstance(self._vtkmapper, vtk.vtkAbstractMapper):
            msg = 'The supplied mapper is a {} but must be a vtk.vtkAbstractMapper type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkmapper).__name__))

        # Create the actor
        self._vtkactor = self.VTKACTORTYPE() if self.VTKACTORTYPE else None
        if (self._vtkactor is not None) and not isinstance(self._vtkactor, vtk.vtkProp):
            msg = 'The supplied actor is a {} but must be a vtk.vtkProp type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkactor).__name__))

        # Connect the mapper and actor and add the actor to the renderer
        if self._vtkmapper is not None:
            self._vtkactor.SetMapper(self._vtkmapper)

        # Storage for the filter objects
        self._filters = list()

        ChiggerAlgorithm.__init__(self, *args, **kwargs)

    def getVTKActor(self):
        """
        Return the constructed vtk actor object. (public)

        Returns:
            An object derived from vtk.vtkProp.
        """
        return self._vtkactor

    def getVTKMapper(self):
        """
        Return the constructed vtk mapper object. (public)

        Returns:
            An object derived from vtk.vtkAbstractMapper
        """
        return self._vtkmapper

    def getFilters(self):
        return self._filters


    #def init(self, vtkactor, vtkmapper):
    #    self.__initialized = True
    #    self._vtkactor = vtkactor
    #    self._vtkmapper = vtkmapper

    def setOptions(self, *args, **kwargs):
        ChiggerAlgorithm.setOptions(self, *args, **kwargs)

        for filter_type in self.__FILTERS__:
            if filter_type.FILTERNAME in args:
                self.__ACTIVE_FILTERS__.add(filter_type.FILTERNAME)

    def applyOptions(self):
        ChiggerAlgorithm.applyOptions(self)
        utils.ActorOptions.applyOptions(self._vtkactor, self._options)

        # Connect the filters
        self.__connectFilters(self._vtkmapper, self._filters)

    def __connectFilters(self, vtkmapper, filters):

        active = []
        connected = False
        for filter_obj in filters:
            if filter_obj.FILTERNAME not in self.__ACTIVE_FILTERS__:
                continue

            active.append(filter_obj)

            if not connected:
                active[-1].SetInputConnection(0, self.GetOutputPort(0))
                connected = True
            else:
                active[-1].SetInputConnection(0, active[-2].GetOutputPort(0))


        # Connect mapper/filters into the pipeline
        if active:
            vtkmapper.SetInputConnection(active[-1].GetOutputPort(0))
        else:
            vtkmapper.SetInputConnection(self.GetOutputPort(0))




#def RequestInformation(self, *args):
#    return 1

#def RequestData(self, *args):
#    self.applyOptions()
#



#TODO: remove
from ChiggerFilterSourceBase import ChiggerFilterSourceBase
class ChiggerSourceOld(ChiggerFilterSourceBase):
    """
    The base class for all 3D objects.

    All VTK settings that can be applied to the (VTKACTOR_TYPE and VTKMAPPER_TYPE) should be made in
    this class.

    Inputs:
        see ChiggerFilterSourceBase
    """

    # The 3D base class actor/mapper that this object to which ownership is restricted
    VTKACTOR_TYPE = vtk.vtkActor
    VTKMAPPER_TYPE = vtk.vtkMapper

    @staticmethod
    def validOptions():
        opt = ChiggerFilterSourceBase.validOptions()
        opt.add('orientation', vtype=float, size=3, doc="The orientation of the object.")
        opt.add('rotation', default=(0., 0., 0.), vtype=float, size=3,
                doc="The rotation of the object about x, y, z axes.")
        opt.add('edges', default=False, doc="Enable/disable display of object edges.")
        opt.add('edge_color', default=(1., 1., 1.), size=3, doc="Set the edge color.")
        opt.add('edge_width', vtype=int, doc="The edge width, if None then no edges are shown.")
        opt.add('point_size', vtype=int, doc="The point size, if None then no points are shown.")
        opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
        opt.add('color', vtype=float, size=3, doc="The color of the object.")
        return opt

    def __init__(self, vtkactor_type=vtk.vtkActor, vtkmapper_type=vtk.vtkPolyDataMapper, **kwargs):
        super(ChiggerSource, self).__init__(vtkactor_type, vtkmapper_type, **kwargs)

    def update(self, **kwargs):
        """
        Updates the VTK settings for the VTKACTOR_TYPE/VTKMAPPER_TYPE objects. (override)

        Inputs:
            see ChiggerFilterSourceBa.se
        """
        super(ChiggerSource, self).update(**kwargs)

        if self.isOptionValid('orientation'):
            self._vtkactor.SetOrientation(self.applyOption('orientation'))

        if self.isOptionValid('rotation'):
            x, y, z = self.applyOption('rotation')
            self._vtkactor.RotateX(x)
            self._vtkactor.RotateY(y)
            self._vtkactor.RotateZ(z)

        if self.isOptionValid('edges') and \
           hasattr(self._vtkactor.GetProperty(), 'SetEdgeVisibility'):
            self._vtkactor.GetProperty().SetEdgeVisibility(self.applyOption('edges'))

        if self.isOptionValid('edge_color') and \
           hasattr(self._vtkactor.GetProperty(), 'SetEdgeColor'):
            self._vtkactor.GetProperty().SetEdgeColor(self.applyOption('edge_color'))

        if self.isOptionValid('edge_width') and \
           hasattr(self._vtkactor.GetProperty(), 'SetLineWidth'):
            self._vtkactor.GetProperty().SetLineWidth(self.applyOption('edge_width'))

        if self.isOptionValid('point_size') and \
           hasattr(self._vtkactor.GetProperty(), 'SetPointSize'):
            self._vtkactor.GetProperty().SetPointSize(self.applyOption('point_size'))

        if self.isOptionValid('opacity'):
            self._vtkactor.GetProperty().SetOpacity(self.applyOption('opacity'))

        if self.isOptionValid('color'):
            self._vtkactor.GetProperty().SetColor(self.applyOption('color'))

    def getBounds(self):
        return self.getVTKMapper().GetBounds()
