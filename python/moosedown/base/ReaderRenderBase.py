class ReaderRenderBase(object):
    def __init__(self, extensions=[]):
        self.__config = dict()
        self.__extensions = extensions
        for ext in self.__extensions:
            ext.setup(self)
            ext.extend()
            for items in ext:
                self.add(*items)

    def reinit(self):
        for ext in self.__extensions:
            ext.reinit()

    def setup(self, config):
        self.__config.update(config)

    def getConfig(self):
        return {key:value[0] for key, value in self.__config.iteritems()}

    def __getitem__(self, name):
        return self.__config[name][0]
