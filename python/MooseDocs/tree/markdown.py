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

from base import NodeBase, Property

class MarkdownNode(NodeBase):
    PROPERTIES = [Property('content', ptype=unicode, required=True)]

    def write(self):
        out = self.content
        for child in self.children:
            out += child.write()
        return out


class Block(MarkdownNode):

    def write(self):
        return '{}\n\n'.format(MarkdownNode.write(self))
