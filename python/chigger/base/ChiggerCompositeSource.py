from ChiggerObject import ChiggerObject
from .. import utils

class ChiggerCompositeSource(utils.KeyBindingMixin, utils.ObserverMixin, ChiggerObject):

    @staticmethod
    def validOptions():
        opt = ChiggerObject.validOptions()
        opt += utils.ObserverMixin.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()
        return bindings

    def __init__(self, *args, **kwargs):
        ChiggerObject.__init__(self, **kwargs)

        self._sources = list()
        for src in args:
            self.addSource(src)

    def addSource(self, src):
        #TODO: check src type

        self._sources.append(src)

    def getVTKActors(self):
        for src in self._sources:
            if src.getVTKActor() is not None:
                yield src.getVTKActor()
