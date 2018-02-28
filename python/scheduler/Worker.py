class Worker(object):
    """
    Worker class for use with scheduler. This is a "mixin" type class that can be used to provide
    scheduling capabilities to arbitrary objects.
    """
    def __init__(self):
        self.__lock

    @property
    def lock(self):
        return self.__lock

    @lock.setter
    def lock(self, value):
        #TODO: type check
        self.__lock = value

    def __call__(self):
        return self.run()

    def run(self):
        raise NotImplementedError
