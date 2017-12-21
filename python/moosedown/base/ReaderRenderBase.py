class ReaderRenderBase(object):
    def __init__(self, extensions=[]):
        self.__config = dict()
        self.__extensions = extensions
        self.__initialized = False

    def init(self, config):
        """
        Called automaticily, do not use
        """
        #TODO: error if called again
        self.update(config)
        for ext in self.__extensions:
            ext.extend()
            for items in ext:
                self.add(*items)
        self.__initialized = True

    def reinit(self):
        for ext in self.__extensions:
            ext.reinit()

    def update(self, config):
        self.__config.update(config)

    def getConfig(self):
        return {key:value[0] for key, value in self.__config.iteritems()}

    def __getitem__(self, name):
        return self.__config[name][0]
