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

class MarkdownNode(LocationNode):
    COLOR = 'CYAN'


root = os.path.join(MooseDocs.ROOT_DIR, 'test', 'docs', 'content')
framework = moose_docs_import(include=['**/Functions/*'],  extension='.md', root=root)
out = [f[len(root):] for f in framework]

root = os.path.join(MooseDocs.ROOT_DIR, 'docs', 'content')
framework = moose_docs_import(include=['**/Functions/framework/*'], extension='.md', root=root)
out += [f[len(root):] for f in framework]


class FileTree(object):


    def __init__(self):
        self._root = LocationNode('')


    def __str__(self):
        return str(anytree.RenderTree(self._root))

    def addNode(self, path):

        def finder(node, name):
            for child in node.children:
                if name == child.name:
                    return child
            return None

        def insert_helper(node, name):
            n = finder(node, name)
            if (n is None) and (name.endswith('.md')):
                n = MarkdownNode(name, parent=node)
            elif (n is None):
                n = LocationNode(name, parent=node)
            return n


        node = self._root
        folders = path.strip('/').split('/')
        for item in folders:
            node = insert_helper(node, item)

tree = FileTree()
for o in out:
    tree.addNode(o)

print tree




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
