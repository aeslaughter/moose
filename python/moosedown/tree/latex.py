"""
Nodes for builing latex.
"""
from base import NodeBase, Property

class Command(NodeBase):
    PROPERTIES = [Property('command', ptype=str, required=True)]

    def write(self):
        out = '\\%s{' % self.command
        for child in self.children:
            out += child.write()
        out += '}'
        return out

class Environment(NodeBase):
    PROPERTIES = [Property('command', ptype=str, required=True)]

    def write(self):
        out = '\\begin{%s}\n' % self.command
        for child in self.children:
            out += child.write()
        out += '\n\\end{%s}' % self.command
        return out

class String(NodeBase):
    """
    A node for containing string content, the parent must always be a Tag.
    """
    PROPERTIES = [Property('content', default='', ptype=str)]

    def write(self):
        out = self.content
        for child in self.children:
            out += child.write()
        return out
