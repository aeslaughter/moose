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
import textwrap
import vtk
import mooseutils

from ChiggerObject import ChiggerObject



#TODO:
# Rename KeyBindingMixin to EventHandler or something
# RenderWindow should have addObserver method, used by update
# FilterResult should have addFilter method, used by update

class ResultEventHandler(object):
    KeyBinding = collections.namedtuple('KeyBinding', 'key shift control alt description function')

    def __init__(self):
        super(ResultEventHandler, self).__init__()
        self.__keybindings = dict()
        self.__active = False
        #
        #self._window = None

        self.addKeyBinding('r', self._nextResult, desc="Select the next result object.")
        self.addKeyBinding('r', self._previousResult, shift=True, desc="Select the previous result object.")
        self.addKeyBinding('h', self._printHelp, desc="Display the help for this object.")



    #def setChiggerRenderWindow(self, window):
    #    self._window = window

    def addKeyBinding(self, key, func, shift=False, control=False, alt=False, desc=None):
        tag = (key, shift, control, alt)
        if tag in self.__keybindings:
            msg = "The key binding '{}' already exists."
            mooseutils.mooseError(msg.format(key))
        else:
            self.__keybindings[tag] = ResultEventHandler.KeyBinding(key, shift, control, alt, desc, func)

    def getKeyBinding(self, key, shift=False, control=False, alt=False):
        return self.__keybindings.get((key, shift, control, alt), None)

    def onSelect(self, active):
        pass

    def onMouseMoveEvent(self):
        pass


    def _nextResult(self, obj, window, binding):
        window.nextActive(1)
        msg = 'Set Active: {}'.format(window.getActive().title())
        print mooseutils.colorText(msg, 'CYAN')

    def _previousResult(self, *args):
        window.nextActive(-1)

    def _printHelp(self, *args):
        """
        Display the available controls for this object.
        """

        # Object name/type
        print mooseutils.colorText(self._title(), 'CYAN')

        # Keybindings
        n = 0
        out = []
        for binding in self.__keybindings.values():
            key = []
            if binding.shift:
                key.append('shift')
            if binding.control:
                key.append('control')
            if binding.alt:
                key.append('alt')
            key.append(binding.key)
            key = '-'.join(key)
            out.append([key, binding.description])
            n = max(n, len(key))

        for key, desc in out:
            key = mooseutils.colorText('{0: >{w}}: '.format(key, w=n), 'GREEN')
            print '\n'.join(textwrap.wrap(desc, 100, initial_indent=key, subsequent_indent=' '*(n + 2)))


class ChiggerResultBase(ChiggerObject, ResultEventHandler):
    """
    Base class for objects to be displayed with a single vtkRenderer object.

    Any object or set of objects that require a single vtkRenderer object should inherit from this
    and all settings for the vtkRender object should be placed in this class.

    If you are creating a new type of "result" object (i.e., something with a vtkRenderer) you will
    likely want to derive from one of the child classes of ChiggerResultBase, such as ChiggerResult.

    Inputs:
        see ChiggerObject
    """


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
