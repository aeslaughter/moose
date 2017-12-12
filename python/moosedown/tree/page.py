"""
Module for text and filename nodes for use by MarkdownReader
"""
import os
import shutil
import logging
import codecs
import types

import base
import mooseutils

LOG = logging.getLogger(__name__)

class PageNodeBase(base.NodeBase):
    COLOR = None
    PROPERTIES = [base.Property('source', ptype=str), base.Property('root', ptype=str)]

    @property
    def local(self):
        path = os.path.join(self.parent.local, self.name) if self.parent else self.name
        return path

    def write(self):
        pass #TODO: unimplemented

    def __repr__(self):
        out = '{} ({}): {}'.format(self.name, self.__class__.__name__, self.source)
        return mooseutils.colorText(out, self.COLOR)

class DirectoryNode(PageNodeBase):
    COLOR = 'CYAN'

    def write(self):
        dst = os.path.join(self.root, self.local)
        if not os.path.isdir(dst):
            os.makedirs(dst)

class FileNode(PageNodeBase):
    PROPERTIES = PageNodeBase.PROPERTIES + [base.Property('content', ptype=unicode)]
    COLOR = 'MAGENTA'

    def write(self):
        dst = os.path.join(self.root, self.local)
        shutil.copyfile(self.source, dst)

class MarkdownStringNode(base.NodeBase):
    PROPERTIES = [base.Property('content', ptype=unicode)]

class MarkdownNode(FileNode): #TODO: Change name to and base creation on file extension being in agreement with Reader
    PROPERTIES = FileNode.PROPERTIES + [base.Property('function')]
    COLOR = 'YELLOW'

    def __init__(self, *args, **kwargs):
        FileNode.__init__(self, *args, **kwargs)

        if os.path.exists(self.source):
            with codecs.open(self.source, encoding='utf-8') as fid:
                self.content = fid.read()

    def write(self):
        if os.path.exists(self.source):
            with codecs.open(self.source, encoding='utf-8') as fid:
                self.content = fid.read()

        print self.content[0:40]

        if self.function:
            html = self.function(self)
        else:
            pass #TODO: error

        dst = os.path.join(self.root, self.local).replace('.md', '.html')  #TODO: MD/HTML should be set from Renderer
        print '{} -> {}'.format(self.source, dst)
        with open(dst, 'w') as fid:
            fid.write(html.write())
