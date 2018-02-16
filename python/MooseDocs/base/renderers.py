"""
Defines Renderer objects that convert AST (from Reader) into an output format.
"""
import os
import re
import logging
import traceback
import anytree

import MooseDocs
from moosedown import common
from MooseDocs.common import exceptions, mixins
from moosedown.tree import html, latex, base, tokens, page

LOG = logging.getLogger(__name__)

class Renderer(mixins.ConfigObject, mixins.TranslatorObject, mixins.ComponentObject):
    """
    Base renderer for converting AST to an output format.
    """

    #:[str] The name of the method to call on RendererComponent objects.
    METHOD = None

    def __init__(self, **kwargs):
        mixins.ConfigObject.__init__(self, **kwargs)
        mixins.TranslatorObject.__init__(self)
        mixins.ComponentObject.__init__(self)
        self.__functions = dict()  # functions on the RenderComponent to call

    def add(self, token, component):
        """
        Associate a RenderComponent object with a token type.

        Inputs:
            token[type]: The token type (not instance) to associate with the supplied component.
            compoment[RenderComponent]: The component to execute with the associated token type.
        """
        common.check_type("token", token, type)
        common.check_type("component", component, MooseDocs.base.components.RenderComponent)
        if self.initialized(): # allow use without Translator object
            component.init(self.translator)
        self.addComponent(component)
        self.__functions[token] = self._method(component)

    def reinit(self):
        """
        Call reinit() method of the RenderComponent objects.
        """
        for comp in self.components:
            comp.reinit()

    def render(self, ast): #pylint: disable=unused-argument
        """
        Render the supplied AST (abstract).

        This method is designed to be overridden to create the desired output tree, see the
        HTMLRenderer and/or LatexRenderer for examples.

        Inputs:
            ast[tree.token]: The AST to convert.
        """
        self.reinit()

    def write(self, output): #pylint: disable=no-self-use
        """
        Write the rendered output content to a single string, this method automatically strips
        all double new lines.

        Inputs:
            output[tree.base.NodeBase]: The output tree created by calling render.
        """
        text = output.write()
        return re.sub(r'(\n{2,})', '\n', text, flags=re.MULTILINE)

    def process(self, parent, token):
        """
        Convert the AST defined in the token input into a output node of parent.

        Inputs:
            ast[tree.token]: The AST to convert.
            parent[tree.base.NodeBase]: A tree object that the AST shall be converted to.
        """
        try:
            func = self.__getFunction(token)
            el = func(token, parent) if func else parent

        except exceptions.RenderException as e:
            el = None
            msg = '\n' + e.message + '\n'
            if token.root.page and token.info:
                msg += "{}:{}".format(token.root.page.source, token.info.line)

            msg += "\nAn error occured while rendering, the error occured when attempting\n"\
                   "to execute the {} function on the {} token.".format(self.METHOD, type(token))

            if token.info:
                LOG.error(MooseDocs.common.box(token.info[0], title=msg, line=token.info.line))
            else:
                LOG.error(msg)

            if tokens.Exception in self.__functions:
                token = tokens.Exception(None, info=token.info, traceback=traceback.format_exc())
                self.process(parent, token)
            else:
                raise exceptions.MooseDocsException(msg)

        if el is not None:
            for child in token.children:
                self.process(el, child)

    def _method(self, component):
        """
        Return the desired method to call on the RenderComponent object.

        Inputs:
            component[RenderComponent]: Object to use for locating desired method for renderering.
        """
        if self.METHOD is None:
            msg = "The Reader class of type {} must define the METHOD class member."
            raise exceptions.MooseDocsException(msg, type(self))
        elif not hasattr(component, self.METHOD):
            msg = "The component object {} does not have a {} method."
            raise exceptions.MooseDocsException(msg, type(component), self.METHOD)
        return getattr(component, self.METHOD)

    def __getFunction(self, token):
        """
        Return the desired function for the supplied token object.

        Inputs:
            token[tree.token]: token for which the associated RenderComponent function is desired.
        """
        return self.__functions.get(type(token), None)

class HTMLRenderer(Renderer):
    """
    Converts AST into HTML.
    """
    METHOD = 'createHTML'

    def render(self, ast):
        """
        Render the supplied AST, wrapping it in a <body> tag.
        """
        self.reinit()
        root = html.Tag(None, 'body', class_='moose-content')
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

    def _method(self, component):
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

    def render(self, ast):
        """
        Convert supplied AST into a Materialize HTML tree.

        Inputs:
            ast[tokens.Token]: The root of the tokenized content to be converted.
        """
        Renderer.render(self, ast) # calls reinit()

        root = html.Tag(None, '!DOCTYPE html', close=False)
        root.page = ast.page #meta data
        html.Tag(root, 'html')

        # <head>
        head = html.Tag(root, 'head')
        html.Tag(head, 'meta', close=False, charset="UTF-8")
        html.Tag(head, 'link', ref="https://fonts.googleapis.com/icon?family=Material+Icons",
                 rel="stylesheet")
        html.Tag(head, 'link', href="/contrib/materialize/materialize.min.css", type="text/css",
                 rel="stylesheet", media="screen,projection")
        html.Tag(head, 'link', href="/contrib/katex/katex.min.css", type="text/css", rel="stylesheet")
        html.Tag(head, 'link', href="/css/moose.css", type="text/css", rel="stylesheet")
        html.Tag(head, 'link', href="/contrib/prism/prism.min.css", type="text/css",
                 rel="stylesheet")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/jquery/jquery.min.js")
        html.Tag(head, 'script', type="text/javascript",
                 src="/contrib/materialize/materialize.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/clipboard/clipboard.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/prism/prism.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/contrib/katex/katex.min.js")
        html.Tag(head, 'script', type="text/javascript", src="/js/init.js")

        body = html.Tag(root, 'body')
        container = html.Tag(body, 'div', class_="container")

        # Breadcrumbs
        if self['breadcrumbs'] and root.page:
            self.addBreadcrumbs(container)

        # Content
        row = html.Tag(container, 'div', class_="row")
        #TODO add scroll spy (scoll-name=False) at top of index.mdg
        col = html.Tag(row, 'div', class_="moose-content col s12 m12 l10")
        HTMLRenderer.process(self, col, ast)

        # Sections
        if self['sections']:
            self.addSections(col, self['collapsible-sections'])

        return root

    @staticmethod
    def addBreadcrumbs(root):
        """
        Inserts breacrumb links at the top of the page.

        Inputs:
            root[tree.html.Tag]: The tag to which the breadcrumbs should be inserted.

        TODO: This is relying on hard-coded .md/.html extensions, that should not be the case.
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
                    url = os.path.relpath(n.local,
                                          os.path.dirname(node.local)).replace('.md', '.html')
                    a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                    html.String(a, content=unicode(n.name))
                else:
                    span = html.Tag(div, 'span', class_="breadcrumb")
                    html.String(span, content=unicode(n.name))

            elif isinstance(n, page.FileNode) and n.name != 'index.md':
                url = os.path.relpath(n.local,
                                      os.path.dirname(node.local)).replace('.md', '.html')
                a = html.Tag(div, 'a', href=url, class_="breadcrumb")
                html.String(a, content=unicode(os.path.splitext(n.name)[0]))

    @staticmethod
    def addSections(root, collapsible):
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
                current = section.get("data-section-level", 0) # get the current section lvel

                if level == current:
                    section = html.Tag(section.parent, 'section')
                elif level > current:
                    section = html.Tag(section, 'section')
                elif level < current:
                    section = html.Tag(section.parent.parent, 'section')

                section['data-section-level'] = level
                if 'data-details-open' in child:
                    section['data-details-open'] = child['data-details-open']

            child.parent = section

        for node in anytree.PreOrderIter(root, filter_=lambda n: n.name == 'section'):

            if 'data-details-open' in node:
                status = node['data-details-open']
            else:
                status = collapsible[node['data-section-level']-1]

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
        self.process(doc, ast)
        return root

    def addPackage(self, *args):
        """
        Add a LaTeX package to the list of packages for rendering.
        """
        self._packages.update(args)
