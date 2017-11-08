"""

"""
from moosedown.tree import html, latex

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

class HTMLRenderer(Renderer):
    METHOD = 'createHTML'

    def render(self, ast, root=None):
        if root is None:
            root = html.Tag('body')
        self.process(ast, root)
        return root

class MaterializeRenderer(HTMLRenderer):
    METHOD = 'createMaterialize'

    def render(self, ast):
        root = html.Tag('html')

        # <head>
        head = html.Tag('head', root)
        icons = html.Tag('link', head, href="https://fonts.googleapis.com/icon?family=Material+Icons", rel="stylesheet")
        materialize =  html.Tag('link', head, type="text/css", rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css",  media="screen,projection")

        body = html.Tag('body', root)
        div = html.Tag('div', body, class_="container")

        HTMLRenderer.render(self, ast, div)

        html.Tag('script', body, type="text/javascript", src="https://code.jquery.com/jquery-3.2.1.min.js")
        html.Tag('script', body, type="text/javascript", src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js")

        return root


class LatexRenderer(Renderer):
    METHOD = 'createLatex'

    def render(self, ast, root=None):
        if root is None:
            root = latex.Environment(command='document')
        self.process(ast, root)
        return root
