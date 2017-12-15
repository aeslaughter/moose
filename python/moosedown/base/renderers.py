"""

"""
import re
import logging
import moosedown
from moosedown.tree import html, latex, base, tokens
from ReaderRenderBase import ReaderRenderBase

LOG = logging.getLogger(__name__)

class Renderer(ReaderRenderBase):
    METHOD = None

    def __init__(self, extensions=None):
        self.__functions = dict()
        ReaderRenderBase.__init__(self, extensions)

    def add(self, token, function):

        if not isinstance(token, type):
            raise TypeError("The supplied token must be a 'type' not an instance.")

        #TODO: check if it exists
        self.__functions[token] = function

    def render(self, ast):
        self.reinit()

    def method(self, component):
        if hasattr(component, self.METHOD):
            return getattr(component, self.METHOD)
        else:
            #TODO: raise RenderException
            pass

    def function(self, token):
        #TODO: error if not found
        for token_type, func in self.__functions.iteritems():
            if isinstance(token, token_type):
                return func
        #if type(token) in self.__functions:
        #    return self.__functions[type(token)]

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
        Renderer.render(self, ast)
        if root is None:
            root = html.Tag(None, 'body')
        self.process(ast, root)
        return root

class MaterializeRenderer(HTMLRenderer):
    METHOD = 'createMaterialize'

    #TODO: Add config

    def method(self, component):
        if hasattr(component, self.METHOD):
            return getattr(component, self.METHOD)
        elif hasattr(component, HTMLRenderer.METHOD):
            return getattr(component, HTMLRenderer.METHOD)
        else:
            #TODO: raise RenderException
            pass

    def render(self, ast, root=None):
        Renderer.render(self, ast)

        if root is None:
            root = html.Tag(None, '!DOCTYPE html', close=False)


        html.Tag(root, 'html')


        # <head>
        head = html.Tag(root, 'head')
        html.Tag(head, 'meta', close=False, charset="UTF-8")
        html.Tag(head, 'link', ref="https://fonts.googleapis.com/icon?family=Material+Icons", rel="stylesheet")
        html.Tag(head, 'link', href="/contrib/materialize/materialize.min.css",  type="text/css", rel="stylesheet", media="screen,projection")
        html.Tag(head, 'link', href="/css/moose.css",  type="text/css", rel="stylesheet")
        html.Tag(head, 'link', href="/contrib/prism/prism.min.css",  type="text/css", rel="stylesheet")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/katex/katex.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/jquery/jquery.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/materialize/materialize.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/clipboard/clipboard.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/prism/prism.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/js/init.js")

        body = html.Tag(root, 'body')
        div = html.Tag(body, 'div', class_="container")

        HTMLRenderer.render(self, ast, div)

        # Add sections
        """
        level = 'h{}'.format(self['section-level'])
        parent = div
        for child in div:
            if child.name == level:
                if parent == div:
                    parent = html.Tag(parent, 'details', class_='scrollspy section')
                else:
                    parent = html.Tag(parent.parent, 'details', class_='scrollspy section')

                #details = html.Tag(parent, 'details')
                summary = html.Tag(parent, 'summary')
                html.Tag(child, 'span', class_='moose-section-icon')
                child.parent = summary

                children = list(child.children[:-1])
                children.insert(0, child.children[-1])
                child.children = children
                #child.children = child.children

            else:
                child.parent = parent
        """
        return root


class LatexRenderer(Renderer):
    METHOD = 'createLatex'

    def __init__(self, *args, **kwargs):
        self._packages = set()
        Renderer.__init__(self, *args, **kwargs)

    def render(self, ast):
        root = base.NodeBase()
        latex.Command(root, 'documentclass', string=u'book', end='\n')

        for package in self._packages:
            latex.Command(root, 'usepackage', string=package, end='\n')


        doc = latex.Environment(root, 'document')
        self.process(ast, doc)
        return root

    def addPackage(self, *args):
        self._packages.update(args)
