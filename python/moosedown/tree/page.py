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
    PROPERTIES = [base.Property('content', ptype=unicode, required=False), base.Property('source', ptype=str)]
    COLOR = None

    def __init__(self, *args, **kwargs):
        base.NodeBase.__init__(self, *args, **kwargs)

    def build(self, translator):
        #TODO: error check content
        translator.convert(self.content)


class LocationNodeBase(PageNodeBase):
    PROPERTIES = PageNodeBase.PROPERTIES + [base.Property('base', ptype=str, default='')]

    def __init__(self, *args, **kwargs):
        PageNodeBase.__init__(self, *args, **kwargs)
        self.name = os.path.basename(self.source)
        self.__cache = dict()

    @property
    def local(self):
        path = os.path.join(self.parent.local, self.name) if self.parent else self.name
        return path

    def findall(self, name, maxcount=None):

        if maxcount and not isinstance(maxcount, int):
            raise TypeError("The 'maxcount' input must be an integer, but '{}' was provided.".format(type(maxcount).__name__))

        try:
            nodes = self.__cache[name]
        except KeyError:
            func = lambda n: n.local.endswith(name)
            nodes = anytree.search.findall(self.root, func)
            self.__cache[name] = nodes
        #func = lambda n: n.local.endswith(name)
        #nodes = anytree.search.findall(self.root, func)


        if maxcount and len(nodes) > maxcount:
            msg = "The 'maxcount' was set to {} but {} nodes were found.".format(maxcount, len(nodes))
            for node in nodes:
                msg += '\n  {} (source: {})'.format(node.local, node.source)
            raise ValueError(msg)

        return nodes

    def __repr__(self):
        out = '{} ({}): {}'.format(self.name, self.__class__.__name__, self.source)
        return mooseutils.colorText(out, self.COLOR)


class DirectoryNode(LocationNodeBase):
    COLOR = 'CYAN'

    def build(self, translator=None):
        dst = os.path.join(self.base, self.local)
        if not os.path.isdir(dst):
            os.makedirs(dst)

class FileNode(LocationNodeBase):
    COLOR = 'MAGENTA'

    #TODO: convert to content property that opens the file if needed
    def read(self):
        if os.path.exists(self.source):
            with codecs.open(self.source, encoding='utf-8') as fid:
                self.content = fid.read()

        #TODO: error if not exist

    def build(self, translator=None):
        dst = os.path.join(self.base, self.local)
        shutil.copyfile(self.source, dst)

class MarkdownNode(FileNode):
#    PROPERTIES = FileNode.PROPERTIES + [base.Property('master', ptype=set, default=set)]

    def __init__(self, *args, **kwargs):
        FileNode.__init__(self, *args, **kwargs)
        self.__master = set()


    @property
    def master(self):
        return self.__master


    def build(self, translator=None):
        for node in self.master:
            node.build(translator)

        self.read()
        ast, html = self.translator.convert(self) #TODO: build cache for html body in translator

        dst = os.path.join(self.base, self.local).replace('.md', '.html')  #TODO: MD/HTML should be set from Renderer
        #LOG.info('%s -> %s', self.source, dst) #TODO: this doesn't work
        print '{} -> {}'.format(self.source, dst)
        with open(dst, 'w') as fid:
            fid.write(html.write())

        return ast, html
