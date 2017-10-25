"""
Nodes for building an HTML tree structure.
"""
import cgi
from base import NodeBase, Property

class Tag(NodeBase):
    def __init__(self, name, parent=None, **kwargs):
        super(Tag, self).__init__(name=name, parent=parent, **kwargs)

    def write(self):
        out = ''
        attr = ' '.join(['{}={}'.format(key, str(value)) for key, value in self.attributes.iteritems() if value])
        if attr:
            out += '<{} {}>'.format(self.name, attr)
        else:
            out += '<{}>'.format(self.name)

        for child in self.children:
            out += child.write()
        out += '</{}>'.format(self.name)
        return out

class String(NodeBase):
    PROPERTIES = [Property('content', default='', ptype=str),
                  Property('escape', default=False, ptype=bool)]

    def write(self):
        if self.escape:
            return cgi.escape(self.content, quote=True)
        else:
            return self.content
