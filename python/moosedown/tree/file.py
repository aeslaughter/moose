"""
Module for text and filename nodes for use by MarkdownReader
"""
import logging
import base

LOG = logging.getLogger(__name__)

class TextNode(base.NodeBase):
    def __init__(self, content, parent):
        super(TextNode, self).__init__()
        self.name = self.__class__.__name__
        self.parent = parent
        self.content = content

    def source(self):
        return 'the current text'


class FileNode(TextNode):
    def __init__(self, filename, parent):

        if not os.path.exists(filename):
            LOG.error("Unknown filename '%s'", filename)

        with open(filename, 'r') as fid:
            content = fid.read()

        super(FileNode, self).__init__(content, parent)
