#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import mooseutils
import chigger
from ChiggerResultBase import ChiggerResultBase
from ChiggerSourceBase import ChiggerSourceBase

class ChiggerResult(ChiggerResultBase):
    """
    A ChiggerResult object capable of attaching an arbitrary number of ChiggerFilterSourceBase
    objects to the vtkRenderer.

    Any options supplied to this object are automatically passed down to the ChiggerFilterSourceBase
    objects contained by this class, if the applicable. To have the settings of the contained source
    objects appear in this objects option dump then simply add the settings to the static getOptions
    method of the derived class. This is not done here because this class is designed to accept
    arbitrary ChiggerFilterSourceBase object which may have varying settings, see ExodusResult for
    an example of a single type implementation based on this class.

    Inputs:
        *sources: A tuple of ChiggerFilterSourceBase object to render.
        **kwargs: see ChiggerResultBase
    """
    # The Base class type that this object to which its ownership is restricted.
    SOURCE_TYPE = ChiggerSourceBase

    @staticmethod
    def validOptions():
        opt = ChiggerResultBase.validOptions()
        return opt

    def __init__(self, *sources, **kwargs):
        super(ChiggerResult, self).__init__(renderer=kwargs.pop('renderer', None), **kwargs)
        self._sources = list()#list(sources)
        #for src in self._sources:
        #    src._parent = self #pylint: disable=protected-access

        for src in sources:
            self.addSource(src)

        self.setOptions(**kwargs)

    def getSources(self):
        return self._sources

    def getBounds(self):
        """
        Return the bounding box of the results.
        """
        self.update()
        return utils.get_bounds(*self._sources)

    def addSource(self, source):
        if not isinstance(source, self.SOURCE_TYPE):
            msg = 'The supplied source type of {} must be of type {}.'
            raise moosecutils.MooseException(msg.format(src.__class__.__name__,
                                                       self.SOURCE_TYPE.__name__))

        self._sources.append(source)
        source.setVTKRenderer(self._vtkrenderer)
        self._vtkrenderer.AddActor(source.getVTKActor())

    def removeSource(self, source):
        source.setVTKRenderer(None)
        selxbf._vtkrenderer.RemoveActor(source.getVTKActor())
        self._sources.remove(source)



    #def needsUpdate(self):
    #    """
    #    Checks if this object or any of the contained ChiggerFilterSourceBase object require update.
    #    (override)
    #    """
    #    return super(ChiggerResult, self).needsUpdate() or \
    #           any([src.needsUpdate() for src in self._sources])

    #def updateOptions(self, *args):
    #    """
    #    Apply the supplied option objects to this object and the contained ChiggerFilterSourceBase
    #    objects. (override)

    #    Inputs:
    #        see ChiggerResultBase
    #    """
    #    changed = [self.needsUpdate()]
    #    changed.append(super(ChiggerResult, self).updateOptions(*args))
    #    for src in self._sources:
    #        changed.append(src.updateOptions(*args))
    #    changed = any(changed)
    #    self.setNeedsUpdate(changed)
    #    return changed

    def setOptions(self, *args, **kwargs):
        """
        Apply the supplied options to this object and the contained ChiggerFilterSourceBase objects.
        (override)

        Inputs:
            see ChiggerResultBase
        """
        super(ChiggerResult, self).setOptions(*args, **kwargs)
        for src in self._sources:
            valid = src.validOptions()
            if args:
                for sub in args:
                    if sub in valid:
                        src.setOptions(sub, **kwargs)
            else:
                for key, value in kwargs.iteritems():
                    if key in src._options:
                        src.setOption(key, value)

    def update(self, **kwargs):
        """
        Update this object and the contained ChiggerFilterSourceBase objects. (override)

        Inputs:
            see ChiggerResultBase
        """
        super(ChiggerResult, self).update(**kwargs)
        for src in self._sources:
            src.update(**kwargs)

    #def setOptions(self, *args, **kwargs):
    #    super(ChiggerResult, self).setOptions(*args, **kwargs)
    #    for src in self._sources:
    #        src.setOptions(*args, **kwargs)

    def getSources(self):
        """
        Return the list of ChiggerSource objects.
        """
        return self._sources

    def reset(self):
        """
        Remove actors from renderer.
        """
        super(ChiggerResult, self).reset()
        for src in self._sources:
            self._vtkrenderer.RemoveActor(src.getVTKActor())

#    def initialize(self):
#        """
#        Initialize by adding actors to renderer.
#        """
#        super(ChiggerResult, self).initialize()
#
#        for src in self._sources:
#            if not isinstance(src, self.SOURCE_TYPE):
#                n = src.__class__.__name__
#                t = self.SOURCE_TYPE.__name__
#                msg = 'The supplied source type of {} must be of type {}.'.format(n, t)
#                raise mooseutils.MooseException(msg)
#            src.setVTKRenderer(self._vtkrenderer)
#            #import traceback; traceback.print_stack()
#            self._vtkrenderer.AddActor(src.getVTKActor())

    def __iter__(self):
        """
        Provides iteration access to the underlying source objects.
        """
        for src in self._sources:
            yield src

    def __getitem__(self, index):
        """
        Provide [] access to the source objects.
        """
        return self._sources[index]

    def __len__(self):
        """
        The number of source objects.
        """
        return len(self._sources)
