#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import logging
import weakref
import vtk
import mooseutils
from ChiggerAlgorithm import ChiggerAlgorithm
from chigger import utils

class ChiggerSource(utils.KeyBindingMixin, utils.ObserverMixin, ChiggerAlgorithm):

    # The type of vtkProp to create (this should be defined in child class)
    VTKACTORTYPE = None

    # The type of vtkAbstractMapper to create (this should be defined in child class)
    VTKMAPPERTYPE = None

    # List of possible filters, this is an internal item. Filters are added with addFilter decorator
    __FILTERS__ = list()

    # List of active filters
    __ACTIVE_FILTERS__ = set()

    # Background options, by default the background color is black thus the default text colors
    # are white. If the background is changed to white then the default text colors are then
    # automatically changed to black
    __BACKGROUND_OPTIONS__ = set()

    @classmethod
    def validOptions(cls):
        opt = ChiggerAlgorithm.validOptions()
        opt += utils.ActorOptions.validOptions()
        opt += utils.ObserverMixin.validOptions()

        """
        opt.add('orientation', vtype=float, size=3, doc="The orientation of the object.")
        opt.add('rotation', default=(0., 0., 0.), vtype=float, size=3,
                doc="The rotation of the object about x, y, z axes.")
        opt.add('edges', default=False, doc="Enable/disable display of object edges.")
        opt.add('edge_color', default=(1., 1., 1.), size=3, doc="Set the edge color.")
        opt.add('edge_width', vtype=int, doc="The edge width, if None then no edges are shown.")
        opt.add('point_size', vtype=int, doc="The point size, if None then no points are shown.")
        opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
        """

        for filter_type in cls.__FILTERS__:
            fname = filter_type.FILTERNAME or filter_type.__name__.lower()
            opt.add(fname,
                    filter_type.validOptions(),
                    doc="Options for the '{}' filter.".format(fname))

        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        return bindings

    def __init__(self, viewport, **kwargs):
        utils.KeyBindingMixin.__init__(self)
        utils.ObserverMixin.__init__(self)
        ChiggerAlgorithm.__init__(self,
                                  #outputType='vtkDataObject',
                                  #nOutputPorts=1,
                                  **kwargs)

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

        # Add this ChiggerSource object to the viewport
        viewport.add(self)

        # Store a reference without reference counting, the underlying VTK objects keep track of
        # things and without the weakref here there is a circular reference between the vtkRenderer
        # and vtkActor objects. The _viewport property should be used by objects that need
        # information from the Viewport object.
        self.__viewport_weakref = weakref.ref(viewport)

    @property
    def _viewport(self):
        """Property so that self._viewport acts like the actual Viewport object."""
        return self.__viewport_weakref()

    def remove(self):
        self.__viewport.remove(self)

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

    def getBounds(self):
        self.Update()
        if isinstance(self._vtkmapper, vtk.vtkPolyDataMapper2D):
            print '2D bounds needs something to do this in general'
            return None
        else:
            return self._vtkmapper.GetBounds()

    def setOptions(self, *args, **kwargs):
        ChiggerAlgorithm.setOptions(self, *args, **kwargs)

        for filter_type in self.__FILTERS__:
            if filter_type.FILTERNAME in args:
                self.__ACTIVE_FILTERS__.add(filter_type.FILTERNAME)

    def applyOptions(self):
        ChiggerAlgorithm.applyOptions(self)
        utils.ActorOptions.applyOptions(self._vtkactor, self._options)

        # Connect the filters
        self.__connectFilters()

        #if self.isOptionValid('orientation'):
        #    self._vtkactor.SetOrientation(self.getOption('orientation'))

        #if self.isOptionValid('rotation'):
        #    x, y, z = self.applyOption('rotation')
        #    self._vtkactor.RotateX(x)
        #    self._vtkactor.RotateY(y)
        #    self._vtkactor.RotateZ(z)

        #if self.isOptionValid('edges') and \
        #   hasattr(self._vtkactor.GetProperty(), 'SetEdgeVisibility'):
        #    self._vtkactor.GetProperty().SetEdgeVisibility(self.getOption('edges'))

        #if self.isOptionValid('edge_color') and \
        #   hasattr(self._vtkactor.GetProperty(), 'SetEdgeColor'):
        #    self._vtkactor.GetProperty().SetEdgeColor(self.getOption('edge_color'))

        #if self.isOptionValid('edge_width') and \
        #   hasattr(self._vtkactor.GetProperty(), 'SetLineWidth'):
        #    self._vtkactor.GetProperty().SetLineWidth(self.getOption('edge_width'))

        #if self.isOptionValid('point_size') and \
        #   hasattr(self._vtkactor.GetProperty(), 'SetPointSize'):
        #    self._vtkactor.GetProperty().SetPointSize(self.getOptions('point_size'))

        #if self.isOptionValid('opacity'):
        #    self._vtkactor.GetProperty().SetOpacity(self.getOption('opacity'))


    def __connectFilters(self):

        base_obj = self
        for filter_obj in self._filters:
            if filter_obj.FILTERNAME in self.__ACTIVE_FILTERS__:
                filter_obj.SetInputConnection(0, base_obj.GetOutputPort(0))
                base_obj = filter_obj

        # Connect mapper/filters into the pipeline
        if self._vtkmapper:
            self._vtkmapper.SetInputConnection(base_obj.GetOutputPort(0))

    def __del__(self):
        ChiggerAlgorithm.__del__(self)

        # Delete the actor and mapper, this is needed to avoid a seg fault in VTK
        self._vtkactor = None
        self._vtkmapper = None
