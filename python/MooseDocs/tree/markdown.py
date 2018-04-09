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
    PROPERTIES = [Property('content', ptype=unicode, required=True)]

    def __init__(self, *args, **kwargs):
        NodeBase.__init__(self, *args, **kwargs)
#        self.location = 0

    def write(self):
        out = self.content
        for child in self.children:
            out += child.write()
        return out


    def length(self):
       return len(self.content)


class Block(MarkdownNode):
    PROPERTIES = [Property('textwrap', ptype=int, default=100)]

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
            if child.content == u' ':
                space = child

            l = child.length()
            if loc + l > self.textwrap:
                space.content = u'\n{}'.format(' '*self.length())
                loc = self.length()
            else:
                loc += l

        # One setting per line
        wrapper = textwrap.TextWrapper(width=self.textwrap)
        for key, value in self.attributes.iteritems():
            if not value:
                continue

            n = len(key) + 1
            wrapper.initial_indent = ' '*self.length()
            wrapper.subsequent_indent = ' '*(self.length() + n)

            out = '\n'.join(wrapper.wrap(u'{}={}'.format(key, value)))
            MarkdownNode(self, content='\n' + out)


        return '{}\n\n'.format(MarkdownNode.write(self))
