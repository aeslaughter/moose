"""

"""
import os
import copy
import re
import logging

import anytree

import moosedown
from moosedown import common
from moosedown.tree import html, latex, base, tokens, page
from extensions import ExtensionObject
from ConfigObject import ConfigObject

LOG = logging.getLogger(__name__)

class Renderer(ConfigObject):
    METHOD = None



    def __init__(self, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        self.__functions = dict()
        self.node = None
        self.translator = None


    def add(self, token, component):
        # TODO: test token_class is type
        component.init(self.translator)
#        self.__components.append(component)
        func = self.__method(component)
#        Extension.add(self, token_class, func)


#    def add(self, token, function):
        #print 'ADD:', token, function


        if not isinstance(token, type):
            raise TypeError("The supplied token must be a 'type' not an instance.")

        print component

        #TODO: check if it exists
        self.__functions[token] = func
        #for k, v in self.__functions.iteritems():
        #    print k, v

    def render(self, ast, reinit=True):
        pass
        #if reinit:
        #    self.reinit()

    def __method(self, component): #TODO: just move to add
        if hasattr(component, self.METHOD):
            return getattr(component, self.METHOD)
        else:
            #TODO: raise RenderException
            pass

    def function(self, token):
        #TODO: error if not found
        #for token_type, func in self.__functions.iteritems():
        #    if isinstance(token, token_type):
        #        return func
        if type(token) in self.__functions:
            return self.__functions[type(token)]

    def write(self, ast):
        text = ast.write()
        return re.sub(r'(\n{2,})', '\n', text, flags=re.MULTILINE)

    def process(self, token, parent):
        try:
            func = self.function(token)
        #    print 'EVAL:', token.name, func
            el = func(token, parent) if func else None
        except Exception as e:
            if token.match:
                msg = "\nAn exception occured while rendering, the exception was raised when\n" \
                      "executing the {} function while processing the following content.\n" \
                      "{}:{}".format(func, 'foo', token.line)
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
    METHOD = 'createHTML' #TODO: make this a config option???

    def render(self, ast, root=None, reinit=True):
        Renderer.render(self, ast, reinit=reinit)
        if root is None:
            root = html.Tag(None, 'body')
        self.process(ast, root)
        return root

class MaterializeRenderer(HTMLRenderer):
    METHOD = 'createMaterialize'

    #TODO: Add config
    @staticmethod
    def defaultConfig():
        config = HTMLRenderer.defaultConfig()
        config['scrollspy'] = (True, "Toggle the use of the right scrollable navigation.")
        config['section-level'] = (2, "The section level for creating collapsible sections and scrollspy.")

        return config


    def method(self, component):
        if hasattr(component, self.METHOD):
            return getattr(component, self.METHOD)
        elif hasattr(component, HTMLRenderer.METHOD):
            return getattr(component, HTMLRenderer.METHOD)
        else:
            #TODO: raise RenderException
            pass

    def render(self, ast, root=None, reinit=True):

        if root is None:
            root = html.Tag(None, '!DOCTYPE html', close=False)


        html.Tag(root, 'html')

        #TODO: create methods for pre/post render tree manipulation


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
        container = html.Tag(body, 'div', class_="container")

        # <nav> Breadcrumbs #TODO: make this a option that can be toggled on a per page (breeadcrumbs=False)
        if self.node: #TODO: access this via translator???

            row = html.Tag(container, 'div', class_="row")
            col = html.Tag(row, 'div', class_="col hide-on-med-and-down l12")
            nav = html.Tag(col, 'nav', class_="breadcrumb-nav")
            div = html.Tag(nav, 'div', class_="nav-wrapper")

            for n in self.node.path:
                if not n.local:
                    continue
                if isinstance(n, page.DirectoryNode):
                    idx = n.find('index.md', maxlevel=2)
                    if idx:
                        url = os.path.relpath(n.local, os.path.dirname(self.node.local)).replace('.md', '.html') #TODO: fix ext
                        a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                        html.String(a, content=unicode(n.name))
                    else:
                        span = html.Tag(div, 'span', class_="breadcrumb")
                        html.String(span, content=unicode(n.name))

                elif isinstance(n, page.FileNode) and n.name != 'index.md':
                    url = os.path.relpath(n.local, os.path.dirname(self.node.local)).replace('.md', '.html') #TODO: fix ext
                    a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                    html.String(a, content=unicode(os.path.splitext(n.name)[0]))




        # Content
        row = html.Tag(container, 'div', class_="row")
        col = html.Tag(row, 'div', class_="col s12 m12 l10") #TODO add scroll spy (scoll-name=False) at top of index.mdg

        HTMLRenderer.render(self, ast, col, reinit=reinit)

        scroll = html.Tag(row, 'div', class_="col l2 hide-on-med-and-down")
        ul = html.Tag(scroll, 'ul', class_="section table-of-contents")

        # Add sections #TODO add toggle
        level = 'h{}'.format(self['section-level'])
        parent = col
        for child in col:
            if child.name == level:
                if parent == col:
                    parent = html.Tag(parent, 'details', class_='scrollspy section', open="open")
                else:
                    parent = html.Tag(parent.parent, 'details', class_='scrollspy section', open="open")

                li = html.Tag(ul, 'li')
                a = html.Tag(li, 'a')
                for c in copy.deepcopy(child.children):
                    c.parent = a

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

        # TODO:Add toggle
        scroll = html.Tag(row, 'div', class_="col l2 hide-on-med-and-down")
        ul = html.Tag(scroll, 'ul', class_="section table-of-contents")


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
