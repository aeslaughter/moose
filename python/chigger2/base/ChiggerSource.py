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

@mooseutils.addProperty('filter_type', required=True)
@mooseutils.addProperty('active', ptype=bool, default=True)
class FilterInfo(mooseutils.AutoPropertyMixin):
    """
    Storage for Filter object information.

    This is a stand-alone class to allow for the 'active' property to be altered.
    """
    pass


class ChiggerSourceBase(utils.KeyBindingMixin, ChiggerAlgorithm):

    # The type of vtkProp to create (this should be defined in child class)
    VTKACTORTYPE = None

    # The type of vtkAbstractMapper to create (this should be defined in child class)
    VTKMAPPERTYPE = None

    # List of possible filters, this is an internal item. Filters are added with addFilter decorator
    #__FILTERS__ = list()

    # List of active filters
    #__ACTIVE_FILTERS__ = set()

    # Background options, by default the background color is black thus the default text colors are
    # white. If the background is changed to white then the default text colors are then
    # automatically changed to black
    __BACKGROUND_OPTIONS__ = set()


    @classmethod
    def validParams(cls):
        opt = ChiggerAlgorithm.validParams()
        opt += utils.KeyBindingMixin.validParams()


        opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
        opt.add('color', vtype=(float, int), size=3, doc="The color of the object.")
        opt.add('linewidth', 1, vtype=(int, float), doc="The line width for the object.")


        opt.add('pointsize', default=1, vtype=(float, int),
                doc="The point size to utilized.")

        # TODO: Restore these
        """
        opt.add('orientation', vtype=float, size=3, doc="The orientation of the object.")
        opt.add('rotation', default=(0., 0., 0.), vtype=float, size=3,
                doc="The rotation of the object about x, y, z axes.")
        """
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        bindings.add('o', ChiggerSourceBase._displayOptions,
                     desc="Output the available options for this object to the screen.")
        bindings.add('o', lambda s: ChiggerSourceBase._displayOptions(s, script=True), shift=True,
                     desc="Output the non-default options for this object, as key-value pairs, to the screen.")
        return bindings

    def __init__(self, viewport, **kwargs):

        # Storage for the available filters for this object, this needs to be before the base
        # class __init__ because the setParams command of this class attempts to apply options to
        # the filters.
        self.__filter_info = list()

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

        # Storage for the filter object instances
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

    def _addFilter(self, filter_type, active=False):
        self.__filter_info.append(FilterInfo(filter_type=filter_type, active=active))

        fname = filter_type.FILTERNAME
        self._options.add(fname, filter_type.validParams(),
                          doc="Options for the '{}' filter.".format(fname))


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
        pass

    def setParams(self, *args, **kwargs):
        ChiggerAlgorithm.setParams(self, *args, **kwargs)

        for finfo in self.__filter_info:
            if finfo.filter_type.FILTERNAME in args:
                finfo.active = True


                self.__ACTIVE_FILTERS__.add(filter_type.FILTERNAME)

    def _onRequestInformation(self):
        ChiggerAlgorithm._onRequestInformation(self)

        # Connect the filters
        self.__connectFilters()

        self.assignParam('color', self._vtkactor.GetProperty().SetColor)
        self.assignParam('opacity', self._vtkactor.GetProperty().SetOpacity)
        self.assignParam('linewidth', self._vtkactor.GetProperty().SetLineWidth)
        self.assignParam('pointsize', self._vtkactor.GetProperty().SetPointSize)

    def _displayOptions(self, script=False):
        if script:
            out, sub_out = self._options.toScriptString()
            print("({})".format(', '.join(out)))
            for key, value in sub_out.items():
                print("'{}', {}".format(key, ', '.join(value)))
        else:
            print(self._options.toString())

    def __connectFilters(self):
        self.debug('__connectFilters')

        for finfo in self.__filter_info:
            fname = finfo.filter_type.FILTERNAME
            if (finfo.active) and (fname not in self._filters):
                self._filters[fname] = finfo.filter_type()
                self.Modified()
            elif (not finfo.active) and (fname in self._filters):
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
    def validParams(cls):
        opt = ChiggerSourceBase.validParams()

        opt.add('representation', default='surface', allow=('surface', 'wireframe', 'points'),
                doc="View volume representation.")

        opt.add('edges', default=False, vtype=bool,
                doc="Enable edges on the rendered object.")
        opt.add('edgecolor', default=(0.5,)*3, array=True, size=3, vtype=float,
                doc="The color of the edges, 'edges=True' must be set.")
        opt.add('edgewidth', default=1, vtype=(float, int),
                doc="The width of the edges, 'edges=True' must be set.")

        opt.add('lines_as_tubes', default=False, vtype=bool,
                doc="Toggle rendering 1D lines as tubes.")

        return opt

    def _onRequestInformation(self):
        ChiggerSourceBase._onRequestInformation(self)

        rep = self.getParam('representation')
        if rep == 'surface':
            self._vtkactor.GetProperty().SetRepresentationToSurface()
        elif rep == 'wireframe':
            self._vtkactor.GetProperty().SetRepresentationToWireframe()
        elif rep == 'points':
            self._vtkactor.GetProperty().SetRepresentationToPoints()

        self.assignParam('edges', self._vtkactor.GetProperty().SetEdgeVisibility)
        self.assignParam('edgecolor', self._vtkactor.GetProperty().SetEdgeColor)
        self.assignParam('edgewidth', self._vtkactor.GetProperty().SetLineWidth)

        self.assignParam('lines_as_tubes', self._vtkactor.GetProperty().SetRenderLinesAsTubes)

    def getBounds(self):
        return self._vtkmapper.GetBounds()


class ChiggerSource2D(ChiggerSourceBase):
    VTKACTORTYPE = vtk.vtkActor2D

    @classmethod
    def validParams(cls):
        opt = ChiggerSourceBase.validParams()

        opt.add('coordinate_system', 'normalized_viewport', vtype=str,
                allow=('normalized_viewport', 'viewport'), doc="Set the input coordinate system.")

        return opt

    def getBounds(self):
        raise NotImplementedError('2D objects must return the bounds as [xmin, xmax, ymin, ymax].')

    def _onRequestInformation(self):
        ChiggerSourceBase._onRequestInformation(self)

        if self._vtkmapper.GetTransformCoordinate() is None:
            self._vtkmapper.SetTransformCoordinate(vtk.vtkCoordinate())
        coordinate = self._vtkmapper.GetTransformCoordinate()
        if self.getParam('coordinate_system') == 'normalized_viewport':
            coordinate.SetCoordinateSystemToNormalizedViewport()
        else:
            coordinate.SetCoordinateSystemToViewport()
