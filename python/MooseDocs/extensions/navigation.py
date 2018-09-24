#pylint: disable=missing-docstring
import os
import uuid
import anytree
import MooseDocs
from MooseDocs.base import components, renderers
from MooseDocs.extensions import command
from MooseDocs.tree import tokens, html
from MooseDocs.tree.base import Property

def make_extension(**kwargs):
    return NavigationExtension(**kwargs)

class NavigationExtension(components.Extension):
    """
    Extension for add navigation items.
    """

    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['items'] = (dict(), "The items to add to the navigation bar.")
        return config

    def extend(self, reader, renderer):
        pass

    def postRender(self, root):


        if isinstance(self.translator.renderer, renderers.MaterializeRenderer):
            header = anytree.search.find_by_attr(root, 'header')
            nav = html.Tag(html.Tag(header, 'nav'), 'div', class_='nav-wrapper container')

            top_ul = html.Tag(nav, 'ul', class_="right hide-on-med-and-down")
            for key, value in self.get('items').iteritems():

                li = html.Tag(top_ul, 'li')
                if isinstance(value, str):
                    href = value if value.startswith('http') else self._findPage(value)
                    html.Tag(li, 'a', href=value, string=unicode(key))

                elif isinstance(value, dict):
                    id_ = uuid.uuid4()
                    a = html.Tag(li, 'a', class_='dropdown-trigger', href='#!', string=unicode(key))
                    a['data-target'] = id_
                    html.Tag(a, 'i', class_='material-icons right', string=u'arrow_drop_down')
                    self._buildDropdown(header, id_, value)

                else:
                    msg = 'Top-level navigation items must be strings.'


    def _findPage(self, path):
        root = self.translator.current.root
        node = root.findall(path)
        if node is None:
            msg = 'Failed to locate navigation item: {}.'.format(value)
            LOG.error(msg)
            raise exceptions.MooseDocsException(msg)
        return node[0].relativeDestination(root)

    def _buildDropdown(self, parent, tag_id, items):
        ul = html.Tag(parent, 'ul', id_=tag_id, class_='dropdown-content')
        for key, value in items.iteritems():
            li = html.Tag(ul, 'li')
            href = value if value.startswith('http') else self._findPage(value)
            html.Tag(li, 'a', href=value, string=unicode(key))
