#pylint: disable=missing-docstring
import uuid
import anytree
import logging
from MooseDocs.base import components, renderers
from MooseDocs.common import exceptions, insert_node_before, insert_node_after
from MooseDocs.tree import tokens, html, page

LOG = logging.getLogger(__name__)

def make_extension(**kwargs):
    return NavigationExtension(**kwargs)

class NavigationExtension(components.Extension):
    """
    Extension for navigation items.
    """

    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['menu'] = (None, "Navigation items, this can either be a menu.md file or a dict. " \
                          "The former creates a 'mega menu' and the later uses dropdowns.")
        return config

    def extend(self, reader, renderer):

        menu = self.get('menu')
        if menu is None:
            msg = "The navigation setting in the MaterializeRenderer is deprecated, " \
                  "please update your code to use the 'menu' setting within the " \
                  "MooseDocs.extensions.navigation extension."
            LOG.warning(msg)
            self.update(menu=self.translator.renderer.get('navigation', None))

    def postRender(self, root):
        """Called after rendering is complete."""

        if isinstance(self.translator.renderer, renderers.MaterializeRenderer):
            header = anytree.search.find_by_attr(root, 'header')
            nav = html.Tag(html.Tag(header, 'nav'), 'div', class_='nav-wrapper container')
            self._addTopNavigation(nav)
            self._addSideNavigation(nav)

    def _addMegaMenu(self, parent, filename):
        """Create a "mega menu" by parsing the *.menu.md file."""

        id_ = uuid.uuid4()
        header = anytree.search.find_by_attr(parent.root, 'header')
        div = html.Tag(header, 'div', id_=id_, class_='moose-mega-menu-content')
        parent['data-target']  = id_

        node = self.translator.current.root.findall(filename)[0]
        node.read()
        ast = tokens.Token(None)
        self.translator.reader.parse(ast, node.content)
        self.translator.renderer.process(div, ast)

    def _addTopNavigation(self, nav):
        """Create navigation in the top bar."""
        ul = html.Tag(nav, 'ul', class_="right hide-on-med-and-down")
        self._createNavigation(ul)

    def _addSideNavigation(self, nav):
        """Adds the hamburger menu for small screens."""
        id_ = uuid.uuid4()

        a = html.Tag(nav, 'a', href='#', class_='sidenav-trigger')
        a['data-target'] = id_
        html.Tag(a, 'i', class_="material-icons", string=u'menu')

        ul = html.Tag(nav, 'ul', class_="sidenav", id_=id_)
        self._createNavigation(ul, mega=False)

    def _createNavigation(self, ul, mega=True):
        """Helper for creating navigation lists."""

        for key, value in self.get('menu').iteritems():

            li = html.Tag(ul, 'li')
            if isinstance(value, str) and value.endswith('menu.md') and mega:
                li['class'] = 'moose-mega-menu-trigger'
                a = html.Tag(li, 'a', string=unicode(key))
                html.Tag(a, 'i', class_='material-icons right', string=u'arrow_drop_down')
                self._addMegaMenu(li, value)

            elif isinstance(value, str):
                href = value if value.startswith('http') else self._findPage(value)
                html.Tag(li, 'a', href=href, string=unicode(key))

            elif isinstance(value, dict):
                id_ = uuid.uuid4()
                a = html.Tag(li, 'a', class_='dropdown-trigger', href='#!', string=unicode(key))
                a['data-target'] = id_
                a['data-constrainWidth'] = 'false'
                html.Tag(a, 'i', class_='material-icons right', string=u'arrow_drop_down')
                self._buildDropdown(ul.parent.parent, id_, value)

            else:
                msg = 'Top-level navigation items must be string or dict.'
                LOG.error(msg)
                raise exceptions.MooseDocsException(msg)

    def _findPage(self, path):
        """Locates page based on supplied path."""
        root = self.translator.current.root
        node = root.findall(path)
        if node is None:
            msg = 'Failed to locate navigation item: {}.'.format(path)
            LOG.error(msg)
            raise exceptions.MooseDocsException(msg)
        return node[0].relativeDestination(root)

    def _buildDropdown(self, parent, tag_id, items):
        """Creates sublist for dropdown navigation."""
        ul = html.Tag(parent, 'ul', id_=tag_id, class_='dropdown-content')
        for key, value in items.iteritems():
            li = html.Tag(ul, 'li')
            href = value if value.startswith('http') else self._findPage(value)
            html.Tag(li, 'a', href=href, string=unicode(key))
