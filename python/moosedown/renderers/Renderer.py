class Renderer(object):
    METHOD = None

    def __init__(self, extensions=None):
        self.__functions = dict()

        if extensions:
            for ext in extensions:
                ext.setup(self)
                ext.extend()
                for items in ext:
                    self.add(*items)

    def add(self, token, function):

        if not isinstance(token, type):
            raise TypeError("The supplied token must be a 'type' not an instance.")

        #TODO: check if it exists
        self.__functions[token] = function

    def render(self, ast):
        pass

    def function(self, token, parent):
        #TODO: error if not found
        if type(token) in self.__functions:
            func = self.__functions[type(token)]
            return func(token, parent)

    def process(self, token, parent):
        el = self.function(token, parent)
        if el is None:
            el = parent
        #TODO: check return type
        for child in token.children:
            self.process(child, el)
