"""
Module for text and filename nodes for use by MarkdownReader
"""
import os
import logging
import codecs

import base
import mooseutils

LOG = logging.getLogger(__name__)

class PageNodeBase(base.NodeBase):
    COLOR = None
    PROPERTIES = [base.Property('source', ptype=str)]

    @property
    def local(self):
        path = os.path.join(self.parent.local, self.name) if self.parent else self.name
        return path

    def __repr__(self):
        out = '{} ({}): {}'.format(self.name, self.__class__.__name__, self.source)
        return mooseutils.colorText(out, self.COLOR)

class DirectoryNode(PageNodeBase):
    COLOR = 'CYAN'

class FileNode(PageNodeBase):
    PROPERTIES = PageNodeBase.PROPERTIES + [base.Property('content', ptype=unicode)]
    COLOR = 'MAGENTA'

    def __init__(self, *args, **kwargs):
        PageNodeBase.__init__(self, *args, **kwargs)

        if os.path.exists(self.source):
            with codecs.open(self.source, encoding='utf-8') as fid:
                self.content = fid.read()

class MarkdownNode(FileNode):
    COLOR = 'YELLOW'
