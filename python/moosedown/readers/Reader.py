from MooseDocs.tree import tokens
class Reader(object):

    def __init__(self, lexer, extensions=None):
        self.__lexer = lexer

        # TODO: make this work, this is the same for Renderer, so there needs to be a base class
        #self.__config = self.getConfig()
        #for ext in extensions:
        #    self.__config.update(ext.getConfig())

        if extensions:
            for ext in extensions:
                ext.setup(self)
                ext.extend()
                for items in ext:
                    self.add(*items)

    @property
    def lexer(self):
        return self.__lexer

    def read(self, filename):
        with open(filename, 'r') as fid:
            text = fid.read()
        return self.parse(text)

    def parse(self, text, root=None):
        ast = root if root else tokens.Token(root)
        self.__lexer.tokenize(text, ast)
        return ast

    def add(self, *args):#name, regex, func, location=-1):
        self.__lexer.add(*args)
