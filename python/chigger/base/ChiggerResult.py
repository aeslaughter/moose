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
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import mooseutils
from chigger import utils
from ChiggerAlgorithm import ChiggerAlgorithm

class ChiggerResult(utils.KeyBindingMixin, ChiggerAlgorithm, VTKPythonAlgorithmBase):
    """
    The ChiggerResult is the base class for creating renderered objects. This class
    contains a single vtkRenderer to which many actors can be added.
    """

    # The type of vtkProp to create (this should be defined in child class)
    VTKACTORTYPE = None

    # The type of vtkAbstractMapper to create (this should be defined in child class)
    VTKMAPPERTYPE = None

    # The type of input (as a string), see PythonAlgoritimBase
    INPUTTYPE = None

    # List of filters, this is an internal item. Filters should be added with addFilter decorator
    __FILTERS__ = list()

    @staticmethod
    def validOptions():
        opt = ChiggerAlgorithm.validOptions()
        opt.add('interactive', default=True,
                doc="Control if the object may be selected with key bindings.")
        opt.add('light', vtype=float,
                doc="Add a headlight with the given intensity to the renderer.")
        opt.add('layer', default=1, vtype=int,
                doc="The VTK layer within the render window.")
        opt.add('viewport', default=(0., 0., 1., 1.), vtype=float, size=4,
                doc="A list given the viewport coordinates [x_min, y_min, x_max, y_max], in " \
                    "relative position to the entire window (0 to 1).")
        opt.add('camera', None, vtype=vtk.vtkCamera,
                doc="The VTK camera to utilize for viewing the results.")
        opt.add('highlight_active', default=True, vtype=bool,
                doc="When the result is activate enable/disable the 'highlighting'.")
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        bindings.add('c', ChiggerResult._printCamera,
                     desc="Display the camera settings for this object.")
        bindings.add('o', lambda s, *args: ChiggerResultBase.printOptions(s),
                     desc="Display the available key, value options for this result.")
        bindings.add('o', lambda s, *args: ChiggerResultBase.printSetOptions(s), shift=True,
                     desc="Display the available key, value options as a 'setOptions' method call.")
        return bindings

    def __init__(self, *args, **kwargs):
        renderer = kwargs.pop('renderer', None)
        utils.KeyBindingMixin.__init__(self)
        ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self)

        # Initialize class members
        self._filters = list()
        self._vtkmappers = list()
        self._vtkactors = list()
        self._vtkrenderer = renderer if renderer is not None else vtk.vtkRenderer()

        # Verify renderer type
        if not isinstance(self._vtkrenderer, vtk.vtkRenderer):
            msg = "The supplied value for the renderer is a {} but it must be of type vtkRenderer."
            raise mooseutils.MooseException(msg.format(type(self._vtkrenderer).__name__))

        # TODO: Restore interactive stuff...
        #self._vtkrenderer.SetInteractive(value)

        # Setup VTKPythobnAlgorithmBase
        self.SetNumberOfInputPorts(len(args))
        self.InputType = self.INPUTTYPE

        for arg in args:
            self.__addSource(arg)

    def __addSource(self, inarg):
        """
        Internal method for adding the necessary filters, mapper, and actor for the input.

        Inputs:
            inarg[vtkPythonAlgorithm]: An algorithm with an output port matching the class
                                       member variable INPUTTYPE.
        """

        # Connect the filters
        filters = []
        connected = False
        for filter_name,filter_type, filter_required in self.__FILTERS__:

            if not filter_required:
                continue

            filters.append(filter_type())

            if not connected:
                filters[-1].SetInputConnection(0, inarg.GetOutputPort(0))
                connected = True
            else:
                filters[-1].SetInputConnection(0, filters[-2].GetOutputPort(0))

        print self.__FILTERS__

        # Create mapper
        vtkmapper = self.VTKMAPPERTYPE() if self.VTKMAPPERTYPE else None
        if (vtkmapper is not None) and not isinstance(vtkmapper, vtk.vtkAbstractMapper):
            msg = 'The supplied mapper is a {} but must be a vtk.vtkAbstractMapper type.'
            raise mooseutils.MooseException(msg.format(type(vtkmapper).__name__))

        # Connect mapper/filters into the pipeline
        if filters:
            vtkmapper.SetInputConnection(filters[-1].GetOutputPort(0))
        else:
            vtkmapper.SetInputConnection(inargs.GetOutputPort(0))

        # TODO: Move
        vtkmapper.SelectColorArray('u')
        vtkmapper.SetScalarModeToUsePointFieldData()
        vtkmapper.InterpolateScalarsBeforeMappingOn()

        # Create the actor
        vtkactor = self.VTKACTORTYPE() if self.VTKACTORTYPE else None
        if (vtkactor is not None) and not isinstance(vtkactor, vtk.vtkProp):
            msg = 'The supplied actor is a {} but must be a vtk.vtkProp type.'
            raise mooseutils.MooseException(msg.format(type(vtkactor).__name__))

        # Connect the mapper and actor and add the actor to the renderer
        if vtkmapper is not None:
            vtkactor.SetMapper(vtkmapper)
        if vtkactor is not None:
            self._vtkrenderer.AddActor(vtkactor)

        # Update the storage of the created objects
        self._filters.append(filters)
        self._vtkmappers.append(vtkmapper)
        self._vtkactors.append(vtkactor)

    def deinit(self):
        """
        Clean up the object prior to removal from RenderWindow.
        """
        for actor in self._vtkactors:
            self._vtkrenderer.RemoveActor(actor)

    #def getBounds(self):
    #    """
    #    Return the bounding box of the results.
    #    """
    #    return utils.get_vtk_bounds_min_max(*[src.getBounds() for src in self._sources])

    #def getRange(self, local=False):
    #    """
    #    Return the min/max range for the selected variables and blocks/boundary/nodeset.

    #    NOTE: For the range to be restricted by block/boundary/nodest the reader must have
    #          "squeeze=True", which can be much slower.
    #    """
    #    rngs = [src.getRange(local=local) for src in self._sources]
    #    return utils.get_min_max(*rngs)

    def getVTKRenderer(self):
        """Return the vtk.vtkRenderer object."""
        return self._vtkrenderer

    def getVTKActor(self, index=-1):
        """
        Return the constructed vtk actor object. (public)

        Returns:
            An object derived from vtk.vtkProp.
        """
        return self._vtkactors[index]

    def getVTKMapper(self, index=-1):
        """
        Return the constructed vtk mapper object. (public)

        Returns:
            An object derived from vtk.vtkAbstractMapper
        """
        return self._vtkmappers[index]

    def getFilters(self, index=-1):
        return self._filters[index]

    #def setActive(self, value):
    #    """
    #    Activate method. This is an internal method, DO NOT USE!

    #    Use RenderWindow.setActive() to activate/deactivate result objects.
    #    """
    #    self._vtkrenderer.SetInteractive(value)
    #    if value and self.getOption('highlight_active'):
    #        if self.__highlight is None:
    #            self.__highlight = chigger.geometric.OutlineResult(self,
    #                                                               interactive=False,
    #                                                               color=(1, 0, 0),
    #                                                               line_width=5)
    #        self.getRenderWindow().append(self.__highlight)

    #    elif self.__highlight is not None:
    #        self.getRenderWindow().remove(self.__highlight)

    def _printCamera(self, *args): #pylint: disable=unused-argument
        """Keybinding callback."""
        print '\n'.join(utils.print_camera(self._vtkrenderer.GetActiveCamera()))

    def __len__(self):
        """
        The number of source objects.
        """
        return len(self._sources)
