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
import collections
import vtk
import mooseutils
from .ChiggerAlgorithm import ChiggerAlgorithm
from .. import utils

class ChiggerSourceBase(utils.KeyBindingMixin, ChiggerAlgorithm):

    # The type of vtkProp to create (this should be defined in child class)
    VTKACTORTYPE = None

    # The type of vtkAbstractMapper to create (this should be defined in child class)
    VTKMAPPERTYPE = None

    # List of possible filters, this is an internal item. Filters are added with addFilter decorator
    __FILTERS__ = list()

    # List of active filters
    __ACTIVE_FILTERS__ = set()

    # Background options, by default the background color is black thus the default text colors are
    # white. If the background is changed to white then the default text colors are then
    # automatically changed to black
    __BACKGROUND_OPTIONS__ = set()

    @classmethod
    def validOptions(cls):
        opt = ChiggerAlgorithm.validOptions()
       # opt += utils.ActorOptions.validOptions()
        opt += utils.KeyBindingMixin.validOptions()


        opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
        opt.add('color', vtype=(float, int), size=3, doc="The color of the object.")
        opt.add('linewidth', 1, vtype=(int, float), doc="The line width for the object.")


        opt.add('lines_as_tubes', default=False, vtype=bool,
                doc="Toggle rendering 1D lines as tubes.")

        opt.add('pointsize', default=1, vtype=(float, int),
                doc="The point size to utilized.")


        # TODO: Use utils.EdgeOptions, obj.setOptions('edges', ...)
        # TODO: Restore these
        """
        opt.add('orientation', vtype=float, size=3, doc="The orientation of the object.")
        opt.add('rotation', default=(0., 0., 0.), vtype=float, size=3,
                doc="The rotation of the object about x, y, z axes.")
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
        ChiggerAlgorithm.__init__(self, **kwargs)

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
        self._filters = collections.OrderedDict()

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
        self._viewport.remove(self)

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
        if isinstance(self._vtkmapper, vtk.vtkPolyDataMapper2D):
            print('2D bounds needs something to do this in general')
            return None
        else:
            return self._vtkmapper.GetBounds()

    def setOptions(self, *args, **kwargs):
        ChiggerAlgorithm.setOptions(self, *args, **kwargs)

        for filter_type in self.__FILTERS__:
            if filter_type.FILTERNAME in args:
                self.__ACTIVE_FILTERS__.add(filter_type.FILTERNAME)

    def _onRequestInformation(self):
        ChiggerAlgorithm._onRequestInformation(self)
        utils.ActorOptions.applyOptions(self._vtkactor, self._options)

        # Connect the filters
        self.__connectFilters()


        self.assignOption('color', self._vtkactor.GetProperty().SetColor)
        self.assignOption('opacity', self._vtkactor.GetProperty().SetOpacity)
        self.assignOption('linewidth', self._vtkactor.GetProperty().SetLineWidth)
        self.assignOption('lines_as_tubes', self._vtkactor.GetProperty().SetRenderLinesAsTubes)
        self.assignOption('pointsize', self._vtkactor.GetProperty().SetPointSize)


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
        self.debug('__connectFilters')

        for filter_type in self.__FILTERS__:
            fname = filter_type.FILTERNAME
            if (fname in self.__ACTIVE_FILTERS__) and (fname not in self._filters):
                self._filters[fname] = filter_type()
                self.Modified()
            elif (fname not in self.__ACTIVE_FILTERS__) and (fname in self._filters):
                self._filters.pop(fname)
                self.Modified()

        base_obj = self
        for fname, filter_obj in self._filters.items():
            self.debug('{} --> {}'.format(base_obj.name(), filter_obj.name()))
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

class ChiggerSource(ChiggerSourceBase):

    VTKACTORTYPE = vtk.vtkActor

    @classmethod
    def validOptions(cls):
        opt = ChiggerSourceBase.validOptions()

        opt.add('representation', default='surface', allow=('surface', 'wireframe', 'points'),
                doc="View volume representation.")

        opt.add('edges', default=False, vtype=bool,
                doc="Enable edges on the rendered object.")
        opt.add('edgecolor', default=(0.5,)*3, array=True, size=3, vtype=float,
                doc="The color of the edges, 'edges=True' must be set.")
        opt.add('edgewidth', default=1, vtype=(float, int),
                doc="The width of the edges, 'edges=True' must be set.")

        return opt


    def _onRequestInformation(self):
        ChiggerSourceBase._onRequestInformation(self)

        rep = self.getOption('representation')
        if rep == 'surface':
            self._vtkactor.GetProperty().SetRepresentationToSurface()
        elif rep == 'wireframe':
            self._vtkactor.GetProperty().SetRepresentationToWireframe()
        elif rep == 'points':
            self._vtkactor.GetProperty().SetRepresentationToPoints()

        self.assignOption('edges', self._vtkactor.GetProperty().SetEdgeVisibility)
        self.assignOption('edgecolor', self._vtkactor.GetProperty().SetEdgeColor)
        self.assignOption('edgewidth', self._vtkactor.GetProperty().SetLineWidth)



class ChiggerSource2D(ChiggerSourceBase):
    VTKACTORTYPE = vtk.vtkActor2D

    @classmethod
    def validOptions(cls):
        opt = ChiggerSourceBase.validOptions()
        return opt
