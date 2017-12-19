"""
Module for text and filename nodes for use by MarkdownReader
"""
import os
import shutil
import logging
import codecs
import types

import anytree

import base
import mooseutils

LOG = logging.getLogger(__name__)

class PageNodeBase(base.NodeBase):
    PROPERTIES = [base.Property('content', ptype=unicode)]
    COLOR = None

    def build(self, translator):
        return translator.convert(self)

    def __repr__(self):
        out = '{} ({}): {}'.format(self.name, self.__class__.__name__, self.source)
        return mooseutils.colorText(out, self.COLOR)

class LocationNodeBase(PageNodeBase):
    PROPERTIES = PageNodeBase.PROPERTIES + [base.Property('source', ptype=str), base.Property('root', ptype=str)]
    __CACHE__ = dict()

    @property
    def local(self):
        path = os.path.join(self.parent.local, self.name) if self.parent else self.name
        return path

    def find(self, name, maxcount=1):
        func = lambda n: n.local.endswith(name)

        # TODO: do this with try cast to avoid double lookup???
        if name in self.__CACHE__:
            nodes = self.__CACHE__[name]
        else:
            nodes = anytree.search.findall(self.root, func)
            self.__CACHE__[name] = nodes

        #TODO: error check

        return nodes

class DirectoryNode(LocationNodeBase):
    COLOR = 'CYAN'

    def build(self, translator=None):
        dst = os.path.join(self.root, self.local)
        if not os.path.isdir(dst):
            os.makedirs(dst)

class FileNode(LocationNodeBase):
    COLOR = 'MAGENTA'

    def build(self, translator=None):
        dst = os.path.join(self.root, self.local)
        shutil.copyfile(self.source, dst)

class MarkdownNode(FileNode):
    def build(self, translator):
        if os.path.exists(self.source):
            with codecs.open(self.source, encoding='utf-8') as fid:
                self.content = fid.read()

        html = translator.convert(self)

        dst = os.path.join(self.root, self.local).replace('.md', '.html')  #TODO: MD/HTML should be set from Renderer
        print '{} -> {}'.format(self.source, dst)
        with open(dst, 'w') as fid:
            fid.write(html.write())
