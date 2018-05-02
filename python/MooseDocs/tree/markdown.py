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
import re

from base import NodeBase, Property

class MarkdownNode(NodeBase):
    def __init__(self, *args, **kwargs):
        NodeBase.__init__(self, *args, **kwargs)

    def write(self):
        content = u''
        for child in self.children:
            content += child.write()
        return content

class Page(MarkdownNode):
    PROPERTIES = [Property('initial_indent', ptype=unicode),
                  Property('subsequent_indent', default=u'', ptype=unicode)]

    def __init__(self, *args, **kwargs):
        MarkdownNode.__init__(self, *args, **kwargs)
        self.__width = 100

        if (self.parent is not None) and (not isinstance(self, Page)):
            raise exceptions.MooseDocsException("Page objects must be children of other Page objects.")

        if self.parent is not None:
            self.__width = self.parent.width - len(self.initial_indent)
        else:
            self.__width -= len(self.initial_indent)

    @property
    def width(self):
        return self.__width

    @property
    def margin(self):
        m = 0
        node = self
        while node.parent is not None:
            node = node.parent
            m += len(self.initial_indent)
        return m

    def write(self):
        content = MarkdownNode.write(self)

        if self.margin:
            content = re.sub(r'^(?=\S)', u' '*self.margin, content, flags=re.MULTILINE)

        if self.initial_indent is not None:
            start = self.margin - len(self.initial_indent)
            content = content[:start] + self.initial_indent + content[self.margin:]

        return content

class Block(MarkdownNode):
    def __init__(self, *args, **kwargs):
        MarkdownNode.__init__(self, *args, **kwargs)
        if not isinstance(self.parent, Page):
            raise exceptions.MooseDocsException("Block objects must be children of Page objects.")

    def write(self):
        return MarkdownNode.write(self) + u'\n'

    @property
    def width(self):
        return self.parent.width

class LineGroup(MarkdownNode):
    def __init__(self, *args, **kwargs):
        MarkdownNode.__init__(self, *args, **kwargs)
        if not isinstance(self.parent, Block):
            raise exceptions.MooseDocsException("LineGroup objects must be children of Block objects.")

    @property
    def width(self):
        return self.parent.width

    def write(self):
        content = MarkdownNode.write(self)
        line = re.sub(r'\s*\n\s*', u' ', content).strip()
        if len(line) < self.width:
            content = line + u'\n'
        return content

class Line(MarkdownNode):
    PROPERTIES = [Property('initial_indent', default=u'', ptype=unicode),
                  Property('subsequent_indent', default=u'', ptype=unicode),
                  Property('padding', default=0, ptype=int),
                  Property('string', ptype=unicode),
                  Property('wrap', ptype=bool, default=True)]

    @property
    def width(self):
        return self.parent.width

    def __init__(self, *args, **kwargs):

        self._wrapper = textwrap.TextWrapper()

        MarkdownNode.__init__(self, *args, **kwargs)

        if not isinstance(self.parent, (Block, LineGroup)):
            raise exceptions.MooseDocsException("Line objects must be children of Block or LineGroup objects.")

        if self.string is not None:
            String(self, content=self.string)

    def write(self):

        items = [child.content for child in self.children if child.content]
        if self.wrap > 0:
            margin = u' '*self.padding
            self._wrapper.initial_indent = u'{}{}'.format(margin, self.initial_indent)
            self._wrapper.subsequent_indent = u'{}{}'.format(margin, self.subsequent_indent)
            self._wrapper.width = self.width

            if items:
                content = u''.join(items)
                content = u'\n'.join(self._wrapper.wrap(content))
            else:
                content = u''
        else:
            return u''.join(items)

        return content + u'\n'

class String(NodeBase):
    PROPERTIES = [Property('content', default=u'', ptype=unicode)]

    def write(self):
        return self.content
