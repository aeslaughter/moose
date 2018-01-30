"""
Defines renderers that convert AST into an output format.
"""
import os
import copy
import re
import logging
import traceback
import anytree

import moosedown
from moosedown import common
from moosedown.common import exceptions
from moosedown.tree import html, latex, base, tokens, page
from ConfigObject import ConfigObject, TranslatorObject

LOG = logging.getLogger(__name__)

class Renderer(ConfigObject, TranslatorObject):
    """
    Base renderer for converting AST to an output format.
    """

    # Method to call on the RendererComponent objects.
    METHOD = None

    def __init__(self, **kwargs):
        ConfigObject.__init__(self, **kwargs)
        TranslatorObject.__init__(self)
        self.__functions = dict()  # functions on the RenderComponent to call
        self.__components = []     # RenderComponent objects

    def add(self, token, component):
        """
        Associate a RenderComponent object with a token type.

        Inputs:
            token[type]: The token type (not instance) to associate with the supplied component.
            compoment[RenderComponent]: The component to execute with the associated token type.
        """

        if not isinstance(token, type):
            msg = "The supplied token must be a {}, but a {} was provided."
            raise exceptions.MooseDocsException(msg, type, type(token))

        if not isinstance(component, moosedown.base.components.RenderComponent):
            msg = "The supplied component must be a {} but a {} was provided."
            raise exceptions.MooseDocsException(msg, moosedown.comonents.RenderComponent,
                                                type(compoment))

        self.__components.append(component)
        self.__functions[token] = self.method(component)

    def method(self, component):
        """
        Return the desired method to call on the RenderComponent object.

        Inputs:
            component[RenderComponent]: Object to use for locating desired method for renderering.
        """
        if not hasattr(component, self.METHOD):
            msg = "The component object {} does not have a {} method."
            raise exceptions.MooseDocsException(msg, type(component), self.METHOD)
        return getattr(component, self.METHOD)

    def reinit(self):
        """
        Call reinit() method of the RenderComponent objects.
        """
        for comp in self.__components:
            comp.reinit()

    def render(self, root, ast):
        """
        Render the supplied AST into the the provided root.

        This method is designed to be overridden to create the desired output tree, see the
        HTMLRenderer and/or LatexRenderer for examples.

        Inputs:
            ast[tree.token]: The AST to convert.
        """
        raise NotImplementedError("The render() method must be defined in a child class.")

    def function(self, token):
        """
        Return the desired function for the supplied token object.

        Inputs:
            token[tree.token]: token for which the associated RenderComponent function is desired.
        """
        try:
            return self.__functions[type(token)]
        except KeyError:
            msg = "The token of type {} was not associated with a RenderComponent function ({}) " \
                  "via the Renderer.add(...) method."
            raise exceptions.RenderException(msg, type(token), self.METHOD)

    def write(self, output):
        """
        Write the rendered output content to a single string, this method automatically strips
        all double new lines.

        Inputs:
            output[tree.base.NodeBase]: The output tree created by calling render.
        """
        text = ast.write()
        return re.sub(r'(\n{2,})', '\n', text, flags=re.MULTILINE)

    def process(self, parent, token):
        """
        Convert the AST defined in the token input into a output node of parent.

        Inputs:
            ast[tree.token]: The AST to convert.
            parent[tree.base.NodeBase]: A tree object that the AST shall be converted to.
        """
        try:
            func = self.function(token)
            el = func(token, parent) if func else None
        except Exception as e:
            src = token.root.page.source if token.root.page else 'fixme' #TODO
            msg = "\nAn exception occured while rendering, the exception was raised when\n" \
                  "executing the {} function while processing the following content.\n" \
                      "{}:{}".format(func, src, token.info.line)
            LOG.exception(moosedown.common.box(token.info[0], title=msg, line=token.info.line))
            token = tokens.Exception(parent, info=token.info, traceback=traceback.format_exc())
            func = self.function(token)
            el = func(token, parent)

        if el is None:
            el = parent

        for child in token.children:
            self.process(child, el)


class HTMLRenderer(Renderer):
    """
    Converts AST into HTML.
    """
    METHOD = 'createHTML' #TODO: make this a config option???

    def render(self, ast):
        self.reinit()
        root = html.Tag(None, 'body')
        self.process(root, ast)
        return root

class MaterializeRenderer(HTMLRenderer):
    """
    Convert AST into HTML using the materialize javascript library (http://materializecss.com).
    """
    METHOD = 'createMaterialize'

    @staticmethod
    def defaultConfig():
        """
        Return the default configuration.
        """
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
        """
        Update the default configuration with the supplied values. This is an override of the
        ConfigObject method and is simply modified here to the check the type of a configuration
        item.
        """
        HTMLRenderer.update(self, **kwargs)

        collapsible = self['collapsible-sections']
        if not isinstance(collapsible, list) or len(collapsible) != 6:
            msg = "The config option 'collapsible-sections' input must be a list of six entries, " \
                  "the item supplied is a {} of length {}."
            raise ValueError(msg.format(type(collapsible), len(collapsible)))

    def method(self, component):
        """
        Fallback to the HTMLRenderer method if the MaterializeRenderer method is not located.

        Inputs:
            component[RenderComponent]: Object to use for locating desired method for renderering.
        """
        if hasattr(component, self.METHOD):
            return getattr(component, self.METHOD)
        elif hasattr(component, HTMLRenderer.METHOD):
            return getattr(component, HTMLRenderer.METHOD)
        else:
            msg = "The component object {} does not have a {} method."
            raise exceptions.MooseDocsException(msg, type(component), self.METHOD)
            exceptions.RenderException()

    def render(self, ast):
        Renderer.render(self, ast) # calls reinit()

        root = html.Tag(None, '!DOCTYPE html', close=False)
        root.page = ast.page #meta data
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

        # Breadcrumbs
        if self['breadcrumbs']:
            self.addBreadcrumbs(container)

        # Content
        row = html.Tag(container, 'div', class_="row")
        col = html.Tag(row, 'div', class_="col s12 m12 l10") #TODO add scroll spy (scoll-name=False) at top of index.mdg
        HTMLRenderer.process(self, col, ast)

        # Sections
        if self['sections']:
            self.addSections(col, self['collapsible-sections'])

        return root

    def addBreadcrumbs(self, root):
        """
        Inserts breacrumb links at the top of the page.

        Inputs:
            root[tree.html.Tag]: The tag to which the breadcrumbs should be inserted.
        """
        row = html.Tag(root, 'div', class_="row")
        col = html.Tag(row, 'div', class_="col hide-on-med-and-down l12")
        nav = html.Tag(col, 'nav', class_="breadcrumb-nav")
        div = html.Tag(nav, 'div', class_="nav-wrapper")

        node = root.root.page
        for n in node.path:
            if not n.local:
                continue
            if isinstance(n, page.DirectoryNode):
                idx = n.find('index.md', maxlevel=2)
                if idx:
                    url = os.path.relpath(n.local, os.path.dirname(node.local)).replace('.md', '.html') #TODO: fix ext
                    a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                    html.String(a, content=unicode(n.name))
                else:
                    span = html.Tag(div, 'span', class_="breadcrumb")
                    html.String(span, content=unicode(n.name))

            elif isinstance(n, page.FileNode) and n.name != 'index.md':
                url = os.path.relpath(n.local, os.path.dirname(node.local)).replace('.md', '.html') #TODO: fix ext
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
    """
    Renderer for converting AST to LaTeX.
    """
    METHOD = 'createLatex'

    def __init__(self, *args, **kwargs):
        self._packages = set()
        Renderer.__init__(self, *args, **kwargs)

    def render(self, ast):
        """
        Built LaTeX tree from AST.
        """
        root = base.NodeBase()
        latex.Command(root, 'documentclass', string=u'book', end='\n')

        for package in self._packages:
            latex.Command(root, 'usepackage', string=package, end='\n')

        doc = latex.Environment(root, 'document')
        self.process(ast, doc)
        return root

    def addPackage(self, *args):
        """
        Add a LaTeX package to the list of packages for rendering.
        """
        self._packages.update(args)
