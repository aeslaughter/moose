#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import collections
import vtk
from ChiggerObject import ChiggerObject

class KeyBindingMixin(object):

    def __init__(self):
        super(KeyBindingMixin, self).__init__()
        self.__keybindings = dict()

        #
        self._window = None

        self.addKeyBinding('r', self._nextResult)
        self.addKeyBinding('r', self._previousResult, shift=True)
        self.addKeyBinding('h', self._help)



    def setChiggerRenderWindow(self, window):
        self._window = window

    def addKeyBinding(self, key, func, shift=False, control=False, alt=False, desc=None):
        key = (key, shift, control, alt)
        if key in self.__keybindings:
            msg = "The key binding '{}' already exists."
            mooseutils.mooseError(msg.format(key))
        else:
            self.__keybindings[key] = ChiggerResultBase.KeyBinding(key, shift, control, alt, desc, func)

    def getKeyBinding(self, key, shift=False, control=False, alt=False):
        return self.__keybindings.get((key, shift, control, alt), None)


    def _nextResult(self):

        self._window.nextActive(1)

    def _previousResult(self):
        self._window.nextActive(-1)

    def _help(self):
        print 'help'


class ChiggerResultBase(ChiggerObject, KeyBindingMixin):
    """
    Base class for objects to be displayed with a single vtkRenderer object.

    Any object or set of objects that require a single vtkRenderer object should inherit from this
    and all settings for the vtkRender object should be placed in this class.

    If you are creating a new type of "result" object (i.e., something with a vtkRenderer) you will
    likely want to derive from one of the child classes of ChiggerResultBase, such as ChiggerResult.

    Inputs:
        see ChiggerObject
    """

    KeyBinding = collections.namedtuple('KeyBinding', 'key shift control alt description function')

    @staticmethod
    def validOptions():
        opt = ChiggerObject.validOptions()

        """
        opt.add('layer', 1, "The VTK layer within the render window.", vtype=int)
        opt.add('viewport', (0., 0., 1., 1.), "A list given the viewport coordinates [x_min, y_min, "
                                          "x_max, y_max], in relative position to the entire "
                                          "window (0 to 1).", vtype=float)
        opt.add('background', (0., 0., 0.), vtype=float,
                doc="The background color, only applied when the 'layer' option is zero. A "
                    "background result is automatically added when chigger.RenderWindow is "
                    "utilized.")
        opt.add('background2', None, "The second background color, when supplied this creates a "
                                     "gradient background, only applied when the 'layer' option is "
                                     "zero. A background result is automatically added when "
                                     "chigger.RenderWindow is utilized.", vtype=float, array=True)
        opt.add('gradient_background', False, "Enable/disable the use of a gradient background.")
        opt.add('camera', None, "The VTK camera to utilize for viewing the results.",
                vtype=vtk.vtkCamera)
        """
        return opt

    def __init__(self, renderer=None, **kwargs):
        super(ChiggerResultBase, self).__init__(**kwargs)
        print 'Renderer:', renderer
        self._vtkrenderer = renderer if renderer != None else vtk.vtkRenderer()



    def getVTKRenderer(self):
        """
        Return the vtkRenderer object. (public)

        Generally, this should not be used. This method if mainly for the RenderWindow object to
        populate the list of renderers that it will be displaying.
        """
        return self._vtkrenderer

    def update(self, **kwargs):
        """
        Update the vtkRenderer settings. (override)

        Inputs:
            see ChiggerObject
        """
        super(ChiggerResultBase, self).update(**kwargs)


        # TODO: Background stuff should be moved to the BackgroundResult...

        """
        # Render layer
        if self.isOptionValid('layer'):
            self._vtkrenderer.SetLayer(self.applyOption('layer'))

        # Viewport
        if self.isOptionValid('viewport'):
            self._vtkrenderer.SetViewport(self.applyOption('viewport'))

        # Background (only gets applied if layer=0)
        if self.isOptionValid('background'):
            self._vtkrenderer.SetBackground(self.applyOption('background'))

        if self.isOptionValid('background2'):
            self._vtkrenderer.SetBackground2(self.applyOption('background2'))

        if self.isOptionValid('gradient_background'):
            self._vtkrenderer.SetGradientBackground(self.applyOption('gradient_background'))

        # Camera
        if self.isOptionValid('camera'):
            self._vtkrenderer.SetActiveCamera(self.applyOption('camera'))
        """
        #self._vtkrenderer.Render()
