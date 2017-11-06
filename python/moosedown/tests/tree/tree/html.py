"""
Nodes for building an HTML tree structure.
"""
import cgi
from base import NodeBase, Property

class Tag(NodeBase):
    """
    A node representing an HTML tag (e.g., h1, strong).
    """
    def __init__(self, name, parent=None, **kwargs):
        super(Tag, self).__init__(name=name, parent=parent, **kwargs)

    def write(self):
        out = ''
        attr = ' '.join(['{}="{}"'.format(key, str(value)) for key, value in self.attributes.iteritems() if value])
        if attr:
            out += '<{} {}>'.format(self.name, attr)
        else:
            out += '<{}>'.format(self.name)

        for child in self.children:
            out += child.write()
        out += '</{}>'.format(self.name)
        return out

class String(NodeBase):
    """
    A node for containing string content, the parent must always be a Tag.
    """
    PROPERTIES = [Property('content', default='', ptype=str),
                  Property('escape', default=False, ptype=bool)]
    def __init__(self, parent=None, **kwargs):
        super(String, self).__init__(parent=parent, **kwargs)

        if (self.parent is not None) and (not isinstance(self.parent, Tag)):
            msg = "If set, the parent of he html.String '{}' must be a html.Tag object, a '{}' " \
                  " was provided."
            raise TypeError(msg.format(self.name, type(self.parent).__name__))

    def write(self):
        if self.escape:
            return cgi.escape(self.content, quote=True)
        else:
            return self.content
