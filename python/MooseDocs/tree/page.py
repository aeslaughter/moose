"""
Module for text and filename nodes for use by MarkdownReader
"""
import os
import shutil
import logging
import codecs
import types

import anytree
import mooseutils

import MooseDocs
from MooseDocs import common
from MooseDocs.common import exceptions, mixins
from MooseDocs.tree import base

LOG = logging.getLogger(__name__)
CACHE = dict() # Create a global cache for faster searching, anytree search is very slow

class PageNodeBase(base.NodeBase, mixins.TranslatorObject):

    PROPERTIES = [base.Property('source', ptype=str)]
    COLOR = None

    def __init__(self, *args, **kwargs):
        mixins.TranslatorObject.__init__(self)
        base.NodeBase.__init__(self, *args, **kwargs)

    def build(self, *args, **kwargs):
        self.write()

    def write(self):
        pass

class LocationNodeBase(PageNodeBase):
    PROPERTIES = [base.Property('base', ptype=str, default='')]

    def __init__(self, *args, **kwargs):
        PageNodeBase.__init__(self, *args, **kwargs)
        _, self.extension = os.path.splitext(self.source)
        self.name = os.path.basename(self.source)

        self.fullpath = os.path.join(self.parent.fullpath, self.name) if self.parent else self.name
        #self.fullpath += self.extension

        CACHE[self.fullpath] = set([self])

    @property
    def local(self):
        return self.fullpath

   # @property
   # def destination(self):
   #     return self.local

    def findall(self, name, maxcount=1, mincount=1, exc=exceptions.MooseDocsException):

        if MooseDocs.LOG_LEVEL == logging.DEBUG:
            common.check_type('name', name, (str, unicode))
            common.check_type('exc', exc, (type, types.LambdaType, type(None)))

        try:
            return list(CACHE[name])

        except KeyError:
            pass

        nodes = set()
        for key in CACHE.keys():
            if key.endswith(name):
                nodes.update(CACHE[key])
        #func = lambda n: n.local.endswith(name)
        #nodes = anytree.search.findall(self.root, filter_=func)
        #self.__cache[name] = nodes

        if maxcount and exc and len(nodes) > maxcount:
            msg = "The 'maxcount' was set to {} but {} nodes were found for the name '{}'.".format(maxcount, len(nodes), name)
            for node in nodes:
                msg += '\n  {} (source: {})'.format(node.local, node.source)
            raise exc(msg)

        elif mincount and exc and len(nodes) < mincount:
            msg = "The 'mincount' was set to {} but {} nodes were found for the name '{}'.".format(mincount, len(nodes), name)
            for node in nodes:
                msg += '\n  {} (source: {})'.format(node.local, node.source)
            raise exc(msg)

        CACHE[name] = nodes
        return list(nodes)

    def relative(self, other):
        """ Location of this page related to the other page."""
        return os.path.relpath(self.local, os.path.dirname(other.local))

    def console(self):
        return '{} ({}): {}'.format(self.name, self.__class__.__name__, self.local)

class DirectoryNode(LocationNodeBase):
    COLOR = 'CYAN'

    def write(self):
        dst = os.path.join(self.base, self.local)
        if not os.path.isdir(dst):
            os.makedirs(dst)

class FileNode(LocationNodeBase):
    COLOR = 'MAGENTA'

    def write(self):
        dst = os.path.join(self.base, self.local)
        shutil.copyfile(self.source, dst)

class MarkdownNode(FileNode):
    PROPERTIES = [base.Property('content', ptype=unicode)]#,
                  #base.Property('master', ptype=set)]

    def __init__(self, *args, **kwargs):
        FileNode.__init__(self, *args, **kwargs)
        #self.master = set() # FIX This...

    def read(self):
        if os.path.exists(self.source):
            LOG.debug('Reading {}'.format(self.source))
            self.content = common.read(self.source)

    @property
    def destination(self):
        return os.path.join(self.base, self.local).replace('.md', '.html')  #TODO: MD/HTML should be set from Renderer

    def relative(self, other):
        """ Location of this page related to the other page."""
        return os.path.relpath(self.destination, os.path.dirname(other.destination))

    def build(self):
        self.translator.build(node)

    def write(self):
        pass
        #if self._html is not None:
        #    dst = self.destination
        #    LOG.debug('Writing %s -> %s', self.source, dst)
        #    with codecs.open(dst, 'w', encoding='utf-8') as fid:
        #        fid.write(self._html.write())
