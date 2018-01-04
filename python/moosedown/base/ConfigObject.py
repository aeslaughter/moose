class ConfigObject(object):

    @staticmethod
    def defaultConfig(config):
        pass


    def __init__(self, **kwargs):
        self.__config = dict()
        self.defaultConfig(self.__config)

        print 'ConfigObject:', self.__config, kwargs
        self.update(**kwargs)


    def update(self, **kwargs):
        unknown = []
        for key, value in kwargs.iteritems():

            if key not in self.__config:
                unknown.append(key)
            else:
                self.__config[key] = (value, self.__config[key][1]) #TODO: type check???

        if unknown:
            msg = "The following config options were not found in the default config options for the {} object:"
            for key in unknown:
                msg += '\n{}{}'.format(' '*4, key)
            raise KeyError(msg.format(type(self)))


    def getConfig(self):
        return {key:value[0] for key, value in self.__config.iteritems()}

    def __getitem__(self, name):
        return self.__config[name][0]
