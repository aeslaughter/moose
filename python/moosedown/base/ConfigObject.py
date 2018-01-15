class ConfigObject(object):

    @staticmethod
    def defaultConfig():
        return dict()

    def __init__(self, **kwargs):
        self.__config = self.defaultConfig()
        #TODO: check self.__config type
        self.update(**kwargs)


    def update(self, **kwargs):

    #    print 'CONFIG:', self.__config
    #    print 'KWARGS:', kwargs

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


    def config(self):
        return self.__config

    def getConfig(self):
        return {key:value[0] for key, value in self.__config.iteritems()}

    def __getitem__(self, name):
        return self.get(name)

    def get(self, name):
        return self.__config[name][0]
