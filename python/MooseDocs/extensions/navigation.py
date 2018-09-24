#pylint: disable=missing-docstring
import uuid
import anytree
import logging
from MooseDocs.base import components, renderers
from MooseDocs.common import exceptions
from MooseDocs.tree import html, page

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
        config['items'] = (dict(), "The items to add to the navigation bar.")
        config['topnav'] = (True, "Enable/disable the navigation in the top navigation bar.")
        config['sidenav'] = (True, "Enable/disable the side navigation for small screens.")
        return config

    def preRender(self, root):
        # mark nodes with .menu.md as inactive

    def postRender(self, root):
        """Called after rendering is complete."""

        if self.translator.current.name == 'maga.md':
            return

        if isinstance(self.translator.renderer, renderers.MaterializeRenderer):
            header = anytree.search.find_by_attr(root, 'header')
            nav = html.Tag(html.Tag(header, 'nav'), 'div', class_='nav-wrapper container')

            if self.get('topnav'):
                self._addTopNavigation(header, nav)

            if self.get('sidenav'):
                self._addSideNavigation(header, nav)

    def _addTopNavigation(self, header, nav):
        """Create navigation in the top bar."""
        ul = html.Tag(nav, 'ul', class_="right hide-on-med-and-down")
        self._createNavigation(ul)

    def _addSideNavigation(self, header, nav):
        """Adds the hamburger menu for small screens."""
        id_ = uuid.uuid4()

        a = html.Tag(nav, 'a', href='#', class_='sidenav-trigger')
        a['data-target'] = id_
        html.Tag(a, 'i', class_="material-icons", string=u'menu')

        ul = html.Tag(nav, 'ul', class_="sidenav", id_=id_)
        self._createNavigation(ul)

    def _createNavigation(self, ul):
        """Helper for creating navigation lists."""

        for key, value in self.get('items').iteritems():

            li = html.Tag(ul, 'li')
            if isinstance(value, str) and value.endswith('|menu'):
                self._buildMegaMenu(value[:-5])

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

    def _buildMegaMenu(self, path):
        root = self.translator.current.root
        node = root.findall(path)[0]

        if self.translator.current.name != node.name:
            print self.translator.current.name, node.name
        #md = page.MarkdownNode(None, source=node.source)
        #md.init(self.translator)
        #ast = md.tokenize()
        #md.render(ast)
        #print md.result
