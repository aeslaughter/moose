"""

"""
import re
import logging
import moosedown
from moosedown.tree import html, latex, base

LOG = logging.getLogger(__name__)

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

    def function(self, token):
        #TODO: error if not found
        if type(token) in self.__functions:
            return self.__functions[type(token)]

    def write(self, ast):
        text = ast.write()
        return re.sub(r'(\n{2,})', '\n', text, flags=re.MULTILINE)

    def process(self, token, parent):
        try:
            func = self.function(token)
            el = func(token, parent) if func else None
        except Exception as e:
            if token.source and token.match:
                msg = "\nAn exception occured while rendering, the exception was raised when\n" \
                      "executing the {} function while processing the following content.\n" \
                      "{}:{}".format(func, token.source, token.line)
                LOG.exception(moosedown.common.box(token.match.group(0), title=msg, line=token.line))
            else:
                msg = "\nAn exception occured on line {} while rendering, the exception was\n" \
                      "raised when executing the {} object while processing the following content.\n"
                msg = msg.format(token.line, token.__class__.__name__)
                LOG.exception(msg)
            raise e

        if el is None:
            el = parent
        #TODO: check return type
        for child in token.children:
            self.process(child, el)

class HTMLRenderer(Renderer):
    METHOD = 'createHTML'

    def render(self, ast, root=None):
        if root is None:
            root = html.Tag(None, 'body')
        self.process(ast, root)
        return root

class MaterializeRenderer(HTMLRenderer):
    METHOD = 'createMaterialize'

    def render(self, ast):
        root = html.Tag(None, '!DOCTYPE html', close=False)
        html.Tag(root, 'html')


        # <head>
        head = html.Tag(root, 'head')
        html.Tag(head, 'meta', close=False, charset="UTF-8")
        html.Tag(head, 'link', ref="https://fonts.googleapis.com/icon?family=Material+Icons", rel="stylesheet")
        html.Tag(head, 'link', href="/contrib/materialize/materialize.min.css",  type="text/css", rel="stylesheet", media="screen,projection")
        html.Tag(head, 'link', href="/contrib/clipboard/clipboard.min.css",  type="text/css", rel="stylesheet")
        html.Tag(head, 'link', href="/contrib/prism/prism.min.css",  type="text/css", rel="stylesheet")
        html.Tag(head, 'link', href="/css/moose.css",  type="text/css", rel="stylesheet")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/katex/katex.min.js") #TODO: Why here, should they all be here
        html.Tag(head, 'script', type="text/javascript", src="/contrib/materialize/materialize.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/clipboard/clipboard.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/prism/prism.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/js/init.js")

        body = html.Tag(root, 'body')
        div = html.Tag(body, 'div', class_="container")

        HTMLRenderer.render(self, ast, div)

        return root


class LatexRenderer(Renderer):
    METHOD = 'createLatex'

    def __init__(self, *args, **kwargs):
        self._packages = set()
        Renderer.__init__(self, *args, **kwargs)

    def render(self, ast):
        root = base.NodeBase()
        latex.Command(root, 'documentclass', string='book', end='\n')

        for package in self._packages:
            latex.Command(root, 'usepackage', string=package, end='\n')


        doc = latex.Environment(root, 'document')
        self.process(ast, doc)
        return root

    def addPackage(self, *args):
        self._packages.update(args)
