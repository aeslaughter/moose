from MooseDocs import tree
from Renderer import Renderer

class HTMLRenderer(Renderer):
    METHOD = 'createHTML'

    def __init__(self, extensions=None):
        super(HTMLRenderer, self).__init__(extensions)

    def render(self, ast, root=None):
        if root is None:
            root = tree.html.Tag('body')
        self.process(ast, root)
        return root

class MaterializeRenderer(HTMLRenderer):
    METHOD = 'createMaterialize'

    def render(self, ast):
        root = tree.html.Tag('html')

        # <head>
        head = tree.html.Tag('head', root)
        icons = tree.html.Tag('link', head, href="https://fonts.googleapis.com/icon?family=Material+Icons", rel="stylesheet")
        materialize = tree.html.Tag('link', head, type="text/css", rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css",  media="screen,projection")

        body = tree.html.Tag('body', root)
        div = tree.html.Tag('div', body, class_="container")

        HTMLRenderer.render(self, ast, div)

        tree.html.Tag('script', body, type="text/javascript", src="https://code.jquery.com/jquery-3.2.1.min.js")
        tree.html.Tag('script', body, type="text/javascript", src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js")

        return root
