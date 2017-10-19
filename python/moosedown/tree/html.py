import cgi
from base import NodeBase

class Tag(NodeBase):
    def __init__(self, name, parent=None, **kwargs):
        super(Tag, self).__init__(parent, **kwargs)
        self.name = name

    def __setitem__(self, key, value):
        key = key.rstrip('_')
        self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes[key]

    def __repr__(self):
        return '{}: {}'.format(self.name, repr(self.attributes))

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
    def __init__(self, content, parent=None, escape=False):
        super(String, self).__init__()
        self.name = self.__class__.__name__
        self.content = content
        self.parent = parent
        if escape:
            self.content = cgi.escape(self.content, quote=True)

    def write(self):
        return self.content

    def __repr__(self):
        return '{}: {}'.format(self.name, self.content)
