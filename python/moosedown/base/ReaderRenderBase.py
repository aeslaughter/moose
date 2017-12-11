class ReaderRenderBase(object):
    def __init__(self, extensions=None):
        self.__config = dict()
        if extensions:
            for ext in extensions:
                ext.setup(self)
                ext.extend()
                for items in ext:
                    self.add(*items)

    def setup(self, config):
        self.__config.update(config)

    def getConfig(self):
        return {key:value[0] for key, value in self.__config.iteritems()}

    def __getitem__(self, name):
        return self.__config[name][0]
