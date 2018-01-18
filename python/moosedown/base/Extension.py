import logging

import moosedown
from moosedown import common
from ConfigObject import ConfigObject

LOG = logging.getLogger(__name__)

class Extension(ConfigObject):

    def __init__(self, **kwargs):
        ConfigObject.__init__(self, **kwargs)
    #    self.__tranlator = None

    #def __copy__(self):
    #    new = type(self)(**self.getConfig())
    #    print new
    #    return new

    @property
    def translator(self):
        return self.__tranlator

    def init(self, translator):
        #TODO: error if called twice
        self.__tranlator = translator

    def extend(self, reader, renderer):
        pass

    def reinit(self):
        pass
