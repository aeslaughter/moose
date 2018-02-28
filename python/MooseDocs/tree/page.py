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
from MooseDocs.tree import base
from MooseDocs.common import exceptions, mixins

LOG = logging.getLogger(__name__)
CACHE = dict()

class PageNodeBase(base.NodeBase, mixins.TranslatorObject):
    PROPERTIES = [base.Property('content', ptype=unicode),
                  base.Property('source', ptype=str)]
    COLOR = None

    def __init__(self, *args, **kwargs):
        mixins.TranslatorObject.__init__(self)
        base.NodeBase.__init__(self, *args, **kwargs)

    #def init(self, translator):
    #    mixins.TranslatorObject.init(self, translator)
    #    for child in self.children:
    #        child.init(translator)

    def build(self, *args, **kwargs):
        self.write()
        #TODO: error check translator
        #translator.convert(self.content)

    def write(self):
        pass

class LocationNodeBase(PageNodeBase):
    PROPERTIES = [base.Property('base', ptype=str, default='')]

    def __init__(self, *args, **kwargs):
        PageNodeBase.__init__(self, *args, **kwargs)
        self.name = os.path.basename(self.source)
        self.fullpath = os.path.join(self.parent.fullpath, self.name) if self.parent else self.name

        CACHE[self.fullpath] = self

    @property
    def local(self):
        return self.fullpath

   # @property
   # def destination(self):
   #     return self.local

    def findall(self, name, exc=exceptions.MooseDocsException):

        if MooseDocs.LOG_LEVEL == logging.DEBUG:
            common.check_type('name', name, (str, unicode))
            common.check_type('exc', exc, type)

        try:
            return CACHE[name]

        except KeyError:
            pass

        nodes = set()
        for key in CACHE.keys():
            if key.endswith(name):
                nodes.add(CACHE[key])
        #func = lambda n: n.local.endswith(name)
        #nodes = anytree.search.findall(self.root, filter_=func)
        #self.__cache[name] = nodes

        maxcount = 1
        mincount = 1
        if maxcount and len(nodes) > maxcount:
            msg = "The 'maxcount' was set to {} but {} nodes were found for the name '{}'.".format(maxcount, len(nodes), name)
            for node in nodes:
                msg += '\n  {} (source: {})'.format(node.local, node.source)
            raise exc(msg)

        elif mincount and len(nodes) < mincount:
            msg = "The 'mincount' was set to {} but {} nodes were found for the name '{}'.".format(mincount, len(nodes), name)
            for node in nodes:
                msg += '\n  {} (source: {})'.format(node.local, node.source)
            raise exc(msg)

        node = list(nodes)[0]
        CACHE[name] = node
        return node

    def relative(self, other):
        """ Location of this page related to the other page."""
        return os.path.relpath(self.local, os.path.dirname(other.local))

    def console(self):
        return '{} ({}): {}'.format(self.name, self.__class__.__name__, self.source)

class DirectoryNode(LocationNodeBase):
    COLOR = 'CYAN'

    def write(self):
        dst = os.path.join(self.base, self.local)
        if not os.path.isdir(dst):
            os.makedirs(dst)

class FileNode(LocationNodeBase):
    COLOR = 'MAGENTA'

    #TODO: convert to content property that opens the file if needed
    def read(self):
        if os.path.exists(self.source):
            with codecs.open(self.source, encoding='utf-8') as fid:
                LOG.debug('Reading {}'.format(self.source))
                self.content = fid.read()

        #TODO: error if not exist

   # def build(self):
    #    self.write()

    def write(self):
        dst = os.path.join(self.base, self.local)
        shutil.copyfile(self.source, dst)

class MarkdownNode(FileNode):
    PROPERTIES = [base.Property('master', ptype=set)]

    def __init__(self, *args, **kwargs):
        FileNode.__init__(self, *args, **kwargs)
        self._ast = None
        self._html = None
        #self._filename = os.path.join(self.base, self.local)
        #self._modified_time = os.path.getmtime(self._filename) #TODO: get this working

        self.master = set()

    def ast(self, reset=False):
        if reset or self._ast is None:
            LOG.debug("Tokenize %s", self.source)
            self._ast = self.translator.ast(self)
        #TODO: error if none, this could be an attribute
        return self._ast

    def render(self, reset=False):
        if reset or self._html is None:
            LOG.debug("Render %s", self.source)
            self._html = self.translator.render(self.ast(reset))

        #TODO: error if none
        return self._html #TODO change name of _html to something better

    def build(self, reset=True):
        LOG.info('Building %s', self.source)

        for node in self.master:
            node.build(reset=reset)

        #mod = os.path.getmtime(self._filename)
        #if (self._ast is None) or (self._html is None) or (mod > self._modified_time):
        self.read()
        #self._ast, self._html = self.translator.convert(self) #TODO: build cache of body within Translator
        #self.ast(reset=True)

        self.render(reset=reset)

        self.write()
        #self._ast = self.translator.ast(self)
        #self._html = self.translator.render(self._ast)
        #self._modified_time = mode

    @property
    def destination(self):
        return os.path.join(self.base, self.local).replace('.md', '.html')  #TODO: MD/HTML should be set from Renderer

    def relative(self, other):
        """ Location of this page related to the other page."""
        return os.path.relpath(self.destination, os.path.dirname(other.destination))

    def write(self):
        if self._html is not None:
            dst = self.destination
            LOG.debug('Writing %s -> %s', self.source, dst)
            with codecs.open(dst, 'w', encoding='utf-8') as fid:
                fid.write(self._html.write())
