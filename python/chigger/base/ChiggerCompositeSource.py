from ChiggerObject import ChiggerObject
from .. import utils

class ChiggerCompositeSource(utils.KeyBindingMixin, ChiggerObject):

    @staticmethod
    def validOptions():
        opt = ChiggerObject.validOptions()
        opt += utils.KeyBindingMixin.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        return bindings

    def __init__(self, *args, **kwargs):
        self._sources = list()
        for src in args:
            self._addSource(src)
        ChiggerObject.__init__(self, **kwargs)

    def _addSource(self, src):
        #TODO: check src type

        self._sources.append(src)

    def applyOptions(self):
        ChiggerObject.applyOptions(self)
        for src in self._sources:
            src.applyOptions()

    def getVTKActors(self):
        for src in self._sources:
            if src.getVTKActor() is not None:
                yield src.getVTKActor()
