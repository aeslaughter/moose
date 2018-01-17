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
    ROOT = None



    def __init__(self, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        self.__functions = dict()
        self.__components = []
        self.translator = None


    def add(self, token, component):
        # TODO: test token_class is type
        self.__components.append(component)
        component.init(self.translator)

        func = self.__method(component)
#        Extension.add(self, token_class, func)

        if not isinstance(token, type):
            raise TypeError("The supplied token must be a 'type' not an instance.")


        #TODO: check if it exists
        self.__functions[token] = func
        #for k, v in self.__functions.iteritems():
        #    print k, v

    def reinit(self):
        for comp in self.__components:
            comp.reinit()


    def render(self, ast, root, reinit=True):
#        self.onPreRender(root)
        self.process(ast, root)
#        self.onPostRender(root)
        return root
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

#    def get(self, name):
#        return self.translator.node.get(name, ConfigObject.get(self, name))


class HTMLRenderer(Renderer):
    METHOD = 'createHTML' #TODO: make this a config option???

    def render(self, ast, root=None, reinit=True):
        if root is None:
            root = html.Tag(None, 'body')
        return Renderer.render(self, ast, root, reinit=reinit)

class MaterializeRenderer(HTMLRenderer):
    METHOD = 'createMaterialize'

    #TODO: Add config
    @staticmethod
    def defaultConfig():
        #config['scrollspy'] = (True, "Toggle the use of the right scrollable navigation.")
        config = HTMLRenderer.defaultConfig()
        config['breadcrumbs'] = (True, "Toggle for the breadcrumb links at the top of page.")
        config['sections'] = (True, "Group heading content into <section> tags.")
        config['collapsible-sections'] = ([None, 'open', None, None, None, None],
                                         "Collapsible setting for the six heading level " \
                                         "sections, possible values include None, 'open', and " \
                                         "'close'. Each indicates if the associated section " \
                                         "should be collapsible, if so should it be open or " \
                                         "closed initially. The 'sections' setting must be " \
                                         "True for this to operate.")
        return config

    def update(self, **kwargs):
        HTMLRenderer.update(self, **kwargs)

        collapsible = self['collapsible-sections']
        if not isinstance(collapsible, list) or len(collapsible) != 6:
            msg = "The config option 'collapsible-sections' input must be a list of six entries, " \
                  "the item supplied is a {} of length {}."
            raise ValueError(msg.format(type(collapsible), len(collapsible)))



    def method(self, component):
        if hasattr(component, self.METHOD):
            return getattr(component, self.METHOD)
        elif hasattr(component, HTMLRenderer.METHOD):
            return getattr(component, HTMLRenderer.METHOD)
        else:
            #TODO: raise Exception
            pass


    def render(self, ast, root=None, reinit=True):
        self.reinit()

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
        container = html.Tag(body, 'div', class_="container")

        #print self.getConfig()

        # Breadcrumbs
        if self['breadcrumbs']:
            self.addBreadcrumbs(container)

        # Content
        row = html.Tag(container, 'div', class_="row")
        col = html.Tag(row, 'div', class_="col s12 m12 l10") #TODO add scroll spy (scoll-name=False) at top of index.mdg
        HTMLRenderer.render(self, ast, col, reinit=reinit)

        # Sections
        if self['sections']:
            self.addSections(col, self['collapsible-sections'])

        return root

    def addBreadcrumbs(self, root):
        """
        Inserts breacrumb links at the top of the page.
        """
        row = html.Tag(root, 'div', class_="row")
        col = html.Tag(row, 'div', class_="col hide-on-med-and-down l12")
        nav = html.Tag(col, 'nav', class_="breadcrumb-nav")
        div = html.Tag(nav, 'div', class_="nav-wrapper")

        for n in self.translator.node.path:
            if not n.local:
                continue
            if isinstance(n, page.DirectoryNode):
                idx = n.find('index.md', maxlevel=2)
                if idx:
                    url = os.path.relpath(n.local, os.path.dirname(self.translator.node.local)).replace('.md', '.html') #TODO: fix ext
                    a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                    html.String(a, content=unicode(n.name))
                else:
                    span = html.Tag(div, 'span', class_="breadcrumb")
                    html.String(span, content=unicode(n.name))

            elif isinstance(n, page.FileNode) and n.name != 'index.md':
                url = os.path.relpath(n.local, os.path.dirname(self.translator.node.local)).replace('.md', '.html') #TODO: fix ext
                a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                html.String(a, content=unicode(os.path.splitext(n.name)[0]))

    def addSections(self, root, collapsible):
        """
        Group content into <section> tags based on the heading tag.

        Inputs:
            root[tree.html.Tag]: The root tree.html node tree to add sections.
            collapsible[list]: A list with six entries indicating the sections to create as
                               collapsible.
        """
        section = root
        for child in section.children:
            if child.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                level = int(child.name[-1])
                current = section.get("data_section_level", 0) # get the current section lvel

                if level == current:
                    section = html.Tag(section.parent, 'section', data_section_level=level)
                elif level > current:
                    section = html.Tag(section, 'section', data_section_level=level)
                elif level < current:
                    section = html.Tag(section.parent.parent, 'section', data_section_level=level)

            child.parent = section

        for node in anytree.PreOrderIter(root, filter_=lambda n: n.name == 'section'):
            status = collapsible[node['data_section_level']-1]
            if status:
                summary = html.Tag(None, 'summary')
                node(0).parent = summary

                details = html.Tag(None, 'details', class_="moose-section-content")
                if status.lower() == 'open':
                    details['open'] = 'open'
                details.children = node.children
                summary.parent = details
                details.parent = node

                icon = html.Tag(None, 'span', class_='moose-section-icon')
                summary(0).children = [icon] + list(summary(0).children)

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
