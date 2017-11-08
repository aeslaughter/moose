"""
Nodes for builing latex.
"""
import re
from base import NodeBase, Property


class Argument(object):
    def __init__(self, prop=None, enclose=('', '')):
        self.prop = prop
        self.enclose = enclose

    def write(self, content):

        out = ''
        if isinstance(content, str):
            out += '{%s}' % content

        elif isinstance(content, NodeBase):
            out += self.enclose[0]
            for child in content.children:
                out += child.write()
            out += self.enclose[1]
        return out


class Mandatory(Argument):
    def __init__(self, *args,  **kwargs):
        Argument.__init__(self, *args, enclose=('{', '}'), **kwargs)

class Optional(object):
    def __init__(self, *args,  **kwargs):
        Argument.__init__(self, *args, enclose=('[', ']'), **kwargs)


class Command(NodeBase):
    PROPERTIES = [Property('arguments', ptype=list, default=[Mandatory]),
                  Property('command', ptype=str, required=True),
                  Property('start', ptype=str, default=''),
                  Property('end', ptype=str, default='')]

    def write(self):
        out = self.start
        out += '\\%s' % self.command
        for arg in self.arguments:
            if arg.prop is None:
                out += arg.write(self)
            else:
                out += arg.write(getattr(self, arg.prop))

        out += self.end
        return out

class Environment(NodeBase):
    PROPERTIES = [Property('command', ptype=str, required=True)]

    def write(self):
        out = '\n\\begin{%s}\n' % self.command
        for child in self.children:
            out += child.write()
        out += '\n\\end{%s}\n' % self.command
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

class Section(Command):
    ARGUMENTS = [Mandatory()]
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, start='\n', end='\n', **kwargs)

class Paragraph(Command):
    ARGUMENTS = [Argument()]
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, command='par', start='\n', end='\n', **kwargs)


class ListItem(Command):
    ARGUMENTS = [Argument()]
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, command='item', start='\n', end=' ', **kwargs)



class Href(Command):
    PROPERTIES = Command.PROPERTIES + [Property('url', ptype=str, required=True)]
    ARGUMENTS = [Mandatory(prop='url'), Mandatory()]

    """
    def write(self):

        out = '\\%s{%s}{' % (self.command, self.url)
        for child in self.children:
            out += child.write()
        out += '}'
        return out
    """
