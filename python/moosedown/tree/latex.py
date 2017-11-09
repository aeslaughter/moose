"""
Nodes for builing latex.
"""
import re
from base import NodeBase, Property

def escape(text):
    """
    Escape LaTeX commands.

    Inputs:
        text: a plain text message
    """
    conv = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '^': '\\^',
        '~': '\\textasciitilde\\',
        '\\': '\\textbackslash\\',
        '<': '\\textless\\',
        '>': '\\textgreater\\',
    }

    regex = re.compile('|'.join(re.escape(unicode(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

class Enclosure(NodeBase):
    """
    Class for enclosing other nodes in characters, e.g. [], {}.
    """
    PROPERTIES = [Property('enclose', ptype=tuple, required=True), Property('string', ptype=str)]

    def __init__(self, *args, **kwargs):
        NodeBase.__init__(self, *args, **kwargs)
        if self.string is not None:
            String(self, content=self.string)

    def write(self):
        out = self.enclose[0]
        for child in self.children:
            out += child.write()
        out += self.enclose[1]
        return out

class Bracket(Enclosure):
    """
    Square bracket enclosure ([]).
    """
    def __init__(self, *args, **kwargs):
        Enclosure.__init__(self, *args, enclose=('[', ']'), **kwargs)

class Brace(Enclosure):
    """
    Curly brace enclosure ({}).
    """
    def __init__(self, *args, **kwargs):
        Enclosure.__init__(self, *args, enclose=('{', '}'), **kwargs)

class InlineMath(Enclosure):
    """
    Math enclosure ($$).
    """
    def __init__(self, *args, **kwargs):
        Enclosure.__init__(self, *args, enclose=('$', '$'), **kwargs)

class Command(NodeBase):
    """
    Typical one argument command: \foo{bar}.
    """
    PROPERTIES = [Property('string', ptype=str),
                  Property('start', ptype=str, default=''),
                  Property('end', ptype=str, default='')]

    def __init__(self, parent, command, *args, **kwargs):
        NodeBase.__init__(self, parent, *args, **kwargs)
        self._command = command
        if not isinstance(self._command, str):
            msg = "The command must be a 'str', but a '{}' was given."
            raise TypeError(msg.format(type(self._command).__name__))

        if self.string is not None:
            String(self, content=self.string)

    def write(self):
        out = self.start
        out += '\\%s{' % self._command
        for child in self.children:
            out += child.write()
        out += '}' + self.end
        return out

    def __repr__(self):
        return '{}: {}'.format(self.name, self._command)

class CustomCommand(Command):
    """
    Class for building up arbitrary commands, with both optional and mandatory arguments.
    """
    PROPERTIES = [Property('start', ptype=str, default=''),
                  Property('end', ptype=str, default='')]

    def write(self):
        out = self.start
        out += '\\%s' % self._command
        for child in self.children:
            out += child.write()
        out += self.end
        return out

class Environment(NodeBase):
    def __init__(self, parent, command, *args, **kwargs):
        NodeBase.__init__(self, parent, *args, **kwargs)
        self._command = command

    def write(self):
        out = '\n\\begin{%s}\n' % self._command
        for child in self.children:
            out += child.write()
        out += '\n\\end{%s}\n' % self._command
        return out

class String(NodeBase):
    """
    A node for containing string content, the parent must always be a Tag.
    """
    PROPERTIES = [Property('content', default='', ptype=str)]

    def write(self):
        out = escape(self.content)
        for child in self.children:
            out += child.write()
        return out
