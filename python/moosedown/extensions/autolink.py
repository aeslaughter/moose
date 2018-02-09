"""Extension for linking to other pages"""
import os
import re
import copy

import anytree

import moosedown
from moosedown.common import exceptions
from moosedown.base import components
from moosedown.extensions import core, table
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return AutoLinkExtension(**kwargs)

class AutoLinkExtension(components.Extension):
    """
    Extension that replaces the default Link and LinkShortcut behavior and handles linking to
    other files. This includes the ability to extract the content from the linked page (i.e.,
    headers) for display on the current page.
    """

    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['include-page-header'] = (True, "Include the linked page top-level header as a " \
                                         "prefix to the auto generated link content when rendering "\
                                         "shortcut linkes.")
        return config

    def extend(self, reader, renderer):
        """Replace default core link components on reader and provide auto link rendering."""

        reader.addInline(AutoLinkComponent(), location='=Link')
        reader.addInline(AutoShortcutLinkComponent(), location='=ShortcutLink')

        renderer.add(AutoLink, RenderAutoLink())
        renderer.add(AutoShortcutLink, RenderAutoShortcutLink())

#: Common regex needed by both components
LINK_RE = re.compile(r'(?P<filename>.*?\.md)(?P<bookmark>#.*)?')

class AutoLinkMixin(object):
    """Common functionality for RenderComponent objects within this class."""

    #: Caches for nodes to avoid searching AST for the same nodes
    BOOKMARK_CACHE = dict()
    HEADING_CACHE = dict()

    def reinit(self):
        AutoLinkMixin.BOOKMARK_CACHE.clear()
        AutoLinkMixin.HEADING_CACHE.clear()

    def createMaterialize(self, token, parent):
        tag = self.createHTML(token, parent)
        tag['class'] = 'tooltipped'
        tag['data-tooltip'] = tag['href']
        tag['data-position'] = 'top'
        return tag

    @staticmethod
    def createHTMLHelper(token, parent, attr):
        """Create the html.Tag and other information needed by RenderComponent objects."""

        # The HTML link tag
        tag = html.Tag(parent, 'a', **token.attributes)

        # Locate the desired page
        exc = lambda msg: exceptions.RenderException(token.info, msg)
        page = token.root.page.findall(getattr(token, attr), maxcount=1, mincount=1, exc=exc)

        # Get the relative path to the page being referenced
        out = os.path.dirname(token.root.page.local)
        href = os.path.relpath(page[0].local, out).replace('.md', '.html')

        return page[0], tag, href


    @staticmethod
    def findToken(ast, token):

        # Load the token from the cache or locate it
        try:
            return AutoLinkMixin.BOOKMARK_CACHE[token.bookmark]
        except KeyError:
            for node in anytree.PreOrderIter(ast):
                if 'id' in node and node['id'] == token.bookmark[1:]:
                    AutoLinkMixin.BOOKMARK_CACHE[token.bookmark] = node
                    return node

        # If you get here the id does not exist
        msg = "Failed to locate a token with id '{}' in '{}'."
        raise exceptions.RenderException(token.info, msg, token.bookmark[1:], ast.root.page.source)

    @staticmethod
    def findHeading(root):
        """Locate the first heading of the supplied AST."""
        try:
            return AutoLinkMixin.HEADING_CACHE[root]
        except KeyError:
            for node in anytree.PreOrderIter(root):
                if isinstance(node, tokens.Heading):
                    AutoLinkMixin.HEADING_CACHE[root] = node
                    return node

class AutoShortcutLink(tokens.ShortcutLink):
    """ShortcutLink token for linking across pages."""
    PROPERTIES = tokens.ShortcutLink.PROPERTIES + [Property('header', default=False),
                                                   Property('bookmark', ptype=unicode)]

class AutoLink(tokens.Link):
    """Link token for linking across pages."""
    PROPERTIES = tokens.Link.PROPERTIES + [Property('bookmark', ptype=unicode)]


class AutoShortcutLinkComponent(core.ShortcutLink):
    """
    Creates an AutoShortcutLink when *.md is detected, otherwise a core.ShortcutLink token.
    """

    def createToken(self, info, parent): #pylint: disable=doc-string
        match = LINK_RE.search(info['key'])
        if match and (parent.root.page is not None):
            return AutoShortcutLink(parent,
                                    key=match.group('filename'),
                                    bookmark=match.group('bookmark'),
                                    header=self.extension['include-page-header'])

        return core.ShortcutLink.createToken(self, info, parent)


class AutoLinkComponent(core.Link):
    """
    Creates an AutoLink when *.md is detected, otherwise a core.Link token.
    """

    def createToken(self, info, parent): #pylint: disable=doc-string
        match = LINK_RE.search(info['url'])
        if match and (parent.root.page is not None):
            return AutoLink(parent, url=match.group('filename'), bookmark=match.group('bookmark'))
        else:
            return core.Link.createToken(self, info, parent)


class RenderAutoLink(AutoLinkMixin, core.RenderLink):
    """Render the AutoLink token."""

    def createHTML(self, token, parent): #pylint: disable=doc-string
        page, tag, href = self.createHTMLHelper(token, parent, 'url')

        if token.bookmark:
            self.findToken(page.ast(), token) # error check
            href += token.bookmark

        tag['href'] = href
        return tag

class RenderAutoShortcutLink(AutoLinkMixin, components.RenderComponent):
    """Render AutoShortcutLink token."""

    def createHTML(self, token, parent): #pylint: disable=doc-string

        page, tag, href = self.createHTMLHelper(token, parent, 'key')
        if token.bookmark is not None:
            tok = self.findToken(page.ast(), token)
            href += token.bookmark

            # Optionally include page header as prefix
            if token.header:
                h = self.findHeading(page.ast())
                if h:
                    for n in h.children:
                        self.translator.renderer.process(tag, n)
                    html.String(tag, content=u':')
        else:
            tok = self.findHeading(page.ast())

        tag['href'] = href
        for n in tok.children:
            self.translator.renderer.process(tag, n)

        return tag
