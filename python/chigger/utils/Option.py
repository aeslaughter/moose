#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
import weakref
import parameters
class Option(parameters.Parameter):
    """
    Custom Parameter object for chigger:

    - includes VTK modified time for the options
    - automatically stores/returns vtkObjects as weakref to avoid cyclic dependencies with VTK

    IMPORTANT:
    VTK objects (i.e., the Viewport to the Window) must be stored without reference counting, the
    underlying VTK objects keep track of things and without the weakref here there is a
    circular reference between the vtkRenderer and vtkRenderWindow objects that is caused by the
    Viewport (vtkRenderer) having a reference to the Window (vtkRenderWindow). Within VTK the
    vtkRenderWindow contains references to the vtkRenderer objects, hence a circular reference
    problem.
    """

    def __init__(self, *args, **kwargs):
        self.__modified = vtk.vtkTimeStamp()                # modified status, see Options class
        parameters.Parameter.__init__(self, *args, **kwargs)
        self.__modified.Modified()

    @property
    def modified(self):
        """Returns the applied status."""
        if hasattr(self._Parameter__value, 'modified'):
            return self._Parameter__value.modified()
        return self.__modified.GetMTime()

    @property
    def value(self):
        """Returns the option value."""
        val = parameters.Parameter.value.fget(self)

        # Handle weakref automatically
        if isinstance(val, weakref.ReferenceType):
            return val()
        return val

    @value.setter
    def value(self, val):
        """
        Sets the value and performs a myriad of consistency checks and updates modified time
        """
        # Automatically convert to Color type
        from .AutoColor import AutoColor, Color #cyclic
        if isinstance(self._Parameter__value, Color):
            old_value = self._Parameter__value._Color__option.value
            self._Parameter__value._Color__option.value = val
            if old_value != val:
                self.__modified.Modified()
            return

        elif (self.vtype is not None) and isinstance(val, tuple):
            if (AutoColor in self.vtype):
                val = AutoColor(*val)
            elif (Color in self.vtype):
                val = Color(*val)

        # Convert vtkObjects to weakref
        if isinstance(val, vtk.vtkObject):
            val = weakref.ref(val)

        old_value = self._Parameter__value
        parameters.Parameter.value.fset(self, val)
        if old_value != self._Parameter__value:
            self.__modified.Modified()
