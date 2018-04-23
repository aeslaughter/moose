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

class Line(NodeBase):
    PROPERTIES = [Property('initial_indent', default=u'', ptype=unicode),
                  Property('subsequent_indent', default=u'', ptype=unicode),
                  Property('width', default=100, ptype=int),
                  Property('margin', default=0, ptype=int)]

    def __init__(self, *args, **kwargs):
        NodeBase.__init__(self, *args, **kwargs)
        self._wrapper = textwrap.TextWrapper()


    def write(self):

        margin = u' '*self.margin
        self._wrapper.initial_indent = u'{}{}'.format(margin, self.initial_indent)
        self._wrapper.subsequent_indent = u'{}{}'.format(margin, self.subsequent_indent)
        self._wrapper.width = self.width

        items = [child.content for child in self.children if child.content]
        if items:
            content = u''.join([child.content for child in self.children if child.content])
            return u'\n'.join(self._wrapper.wrap(content)) + u'\n'
        else:
            return ''

class String(NodeBase):
    PROPERTIES = [Property('content', default=u'', ptype=unicode)]
    def write(self):
        return self.content

class Break(NodeBase):
    PROPERTIES = [Property('count', default=1, ptype=int)]

    def write(self):
        return u'\n'*self.count

class Block(Line):

    def write(self):

        content = Line.write(self)

        single = content.replace('\n', ' ')
        if len(single) < self.width - self.margin:
            return single

        return content

#class Space(NodeBase):
#    def write(self):
#        return u' '



"""
class MarkdownNode(NodeBase):
    PROPERTIES = [Property('content', ptype=list, required=False, default=u''),
                  Property('indent', ptype=int, default=0)]


    def write(self):
        out = self.content
        for child in self.children:
            out += child.write()
        return '\n'.join(out)

    def length(self):
       return len(self.content) + self.indent

    @property
    def indent(self):
        return sum([a.indent for a in self.anscestors])
"""

"""
class Block(MarkdownNode):
    PROPERTIES = [Property('textwrap', ptype=int, default=100),
                  Property('count', ptype=int, default=2)]

    def write(self):
        lines = []


        width = self.textwrap - self.indent

        # If the rendered output fits on a line, just write it out
        # TODO: Make this configure option
        output = MarkdownNode.write(self)
        for key, value in self.attributes.iteritems():
            if value:
                output += u' {}={}'.format(key, value)

        if len(output) < width:
            return [output, '', '']#{}\n\n'.format(output)

        # Wrap content
        loc = self.length()
        space = None
        for child in self.children:
            if isinstance(child, Space):
                space = child

            #print loc, self.textwrap, child.content
            loc += child.length()
            if loc > width:
                space.content = u'\n{}'.format(' '*self.length())
                loc = child.length()# + child.length()

        # One setting per line
        wrapper = textwrap.TextWrapper(width=width)
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
        self.indent = len(self.prefix)
"""
"""
def write(self):
for i, child in enumerate(self.children):
if i == 0:
child.content = self.prefix
else:
child.content = u' '*len(self.prefix)
child.count = 0
return MarkdownNode.write(self)
"""
