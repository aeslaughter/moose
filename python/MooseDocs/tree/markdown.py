#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
#pylint: enable=missing-docstring
import textwrap

from base import NodeBase, Property

class MarkdownNode(NodeBase):
    PROPERTIES = [Property('content', ptype=unicode, required=False, default=u''),
                  Property('indent', ptype=int, default=0)]


    def write(self):
        out = self.content
        for child in self.children:
            out += ' '*self.indent + child.write()
        return out

    def length(self):
       return len(self.content) + self.indent

    def indent(self):
        return sum([a.indent for a in self.anscestors])

class Block(MarkdownNode):
    PROPERTIES = [Property('textwrap', ptype=int, default=100),
                  Property('count', ptype=int, default=2)]

    def write(self):

        # If the rendered output fits on a line, just write it out
        # TODO: Make this configure option
        output = MarkdownNode.write(self)
        for key, value in self.attributes.iteritems():
            if value:
                output += u' {}={}'.format(key, value)
        if len(output) < self.textwrap:
            return '{}\n\n'.format(output)

        # Wrap content
        loc = self.length()
        space = None
        for child in self.children:
            if isinstance(child, Space):
                space = child

            #print loc, self.textwrap, child.content
            loc += child.length()
            if loc > self.textwrap:
                space.content = u'\n{}'.format(' '*self.length())
                loc = child.length()# + child.length()

        # One setting per line
        wrapper = textwrap.TextWrapper(width=self.textwrap)
        for key, value in self.attributes.iteritems():
            if not value:
                continue

            n = len(key) + 1
            wrapper.initial_indent = ' '*self.length()
            wrapper.subsequent_indent = ' '*(self.length() + n)

            out = '\n'.join(wrapper.wrap(u'{}={}'.format(key, value)))
            Break(self, count=1)
            MarkdownNode(self, content=out)

        if self.count > 0:
            Break(self, count=self.count)
        return '{}'.format(MarkdownNode.write(self))

class String(MarkdownNode):
    pass

class Space(MarkdownNode):
    def __init__(self, *args, **kwargs):
        MarkdownNode.__init__(self, *args, content=u' ', **kwargs)

class Break(MarkdownNode):
    PROPERTIES = [Property('count', ptype=int, default=1)]

    def __init__(self, *args, **kwargs):
        MarkdownNode.__init__(self, *args, content=u'\n', **kwargs)

    def write(self):
        out = self.content * self.count
        for child in self.children:
            out += child.write()
        return out

class List(MarkdownNode):
    pass

class ListItem(MarkdownNode):
    PROPERTIES = [Property('prefix', ptype=unicode, required=True)]

    def __init__(self, *args, **kwargs):
        MarkdownNode.__init__(self, *args, **kwargs)
        #self.indent = len(self.prefix)

    def write(self):
        for i, child in enumerate(self.children):
            if i == 0:
                child.content = self.prefix
            else:
                child.content = u' '*len(self.prefix)
                child.count = 0
        return MarkdownNode.write(self)
