"""
Module for text and filename nodes for use by MarkdownReader
"""
import logging
import codecs

import base

LOG = logging.getLogger(__name__)

class FileNode(base.NodeBase):
    PROPERTIES = [base.Property('source', ptype=str), base.Property('content', ptype=str)]

    def __init__(self, *args, **kwargs):
        base.NodeBase.__init__(self, *args, **kwargs)

        if os.path.exists(self.source):
            with codes.open(self.source, encoding='utf-8') as fid:
                self.content = fid.read()

"""
class FileNode(TextNode):
    def __init__(self, filename, parent):

        if not os.path.exists(filename):
            LOG.error("Unknown filename '%s'", filename)

        with open(filename, 'r') as fid:
            content = fid.read()

        super(FileNode, self).__init__(content, parent)
"""
