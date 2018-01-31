"""
"""
import re
import uuid
import importlib
import collections

from moosedown import base, common
from moosedown.extensions import core, command, floats
from moosedown.tree import html, latex, tokens
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return IncludeExtension()

class IncludeExtension(command.CommandExtension):

    def extend(self, reader, renderer):
        self.addCommand(Include())

class Include(command.CommandComponent):
    COMMAND = 'include'
    SUBCOMMAND = 'md'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        return settings

    def createToken(self, match, parent):

        #print parent.node

        #print self.reader.node, type(self.reader.node), match.groups()

        node = parent.node.findall(match.group('filename'), maxcount=1)[0]
        node.read()

        #TODO: check type of node, must be markdown for this to work or the node needs to be created

        # Set the master node, so that when livereload fires on this included node that the
        # node that does the including is reloaded
        node.master.add(parent.node)
        #print node.name, parent.node.name, node.master

        ast = self.reader.parse(node)
        for child in ast.children:
            child.parent = parent
        return parent
