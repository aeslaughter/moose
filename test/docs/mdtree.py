#!/usr/bin/env python
import os
import collections
import mooseutils
import MooseDocs
from MooseDocs.common.MooseAppSyntax import MooseDocsNodeBase
from MooseDocs.common import moose_docs_import

import anytree

class LocationNode(MooseDocsNodeBase):
    COLOR = 'YELLOW'
    def __init__(self, name, root=None, group=None, **kwargs):
        super(LocationNode, self).__init__(name, **kwargs)
        self._root = root
        self._group = group

class MarkdownNode(LocationNode):
    COLOR = 'CYAN'

    @property
    def filename(self):
        return os.path.join(self._root, self.full_name.strip('/'))


config = dict()
config['framework'] = dict(base='docs/content', include=['**/Functions/framework/*'])
config['moose_test'] = dict(base='test/docs/content', include=['**/Functions/*'])



class FileTree(object):


    def __init__(self, config):


        self._root = MooseDocsNodeBase('')


        for key, value in config.iteritems():
            value.setdefault('root', MooseDocs.abspath(value.pop('base', '')))
            value.setdefault('extension', '.md')

            files = moose_docs_import(**value)
            for filename in files:
                print value
                self.addNode(value['root'], filename, group=key)

    def __str__(self):
        return str(anytree.RenderTree(self._root))

    def addNode(self, root, path, group):

        def finder(node, name):
            for child in node.children:
                if name == child.name:
                    return child
            return None

        def insert_helper(node, name):
            n = finder(node, name)
            if (n is None) and (name.endswith('.md')):
                n = MarkdownNode(name, root=root, group=group, parent=node)
            elif (n is None):
                n = LocationNode(name, root=root, group=group, parent=node)
            return n


        node = self._root
        folders = path[len(root):].strip('/').split('/')
        for item in folders:
            node = insert_helper(node, item)

tree = FileTree(config)
print tree

for c in tree._root.descendants:
    if isinstance(c, MarkdownNode):
        print c.filename
    #if hasattr(c, 'filename'):
    #    print c#.filename





"""

r = anytree.Node()



data = collections.defaultdict(lambda: collections.defaultdict(str))
def add_node(input):
    filename = os.path.basename(input)
    folders = os.path.dirname(input).strip('/').split('/')
    brackets = ("['{}']"*len(folders)).format(*folders)
    eval("data{}='{}'".format(brackets, filename))

add_node(files[0])

print data
"""
