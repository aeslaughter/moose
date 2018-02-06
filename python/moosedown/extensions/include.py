"""
"""
import re
import uuid
import importlib
import collections

from moosedown import common
from moosedown.base import components
from moosedown.extensions import core, command, floats
from moosedown.tree import html, latex, tokens, page
from moosedown.tree.base import Property

class IncludeToken(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + \
                 [Property("include", ptype=page.MarkdownNode, required=True)]

def make_extension(**kwargs):
    return IncludeExtension()

class IncludeExtension(command.CommandExtension):

    def extend(self, reader, renderer):
        self.addCommand(Include())
        renderer.add(IncludeToken, RenderInclude())

class Include(command.CommandComponent):
    COMMAND = 'include'
    SUBCOMMAND = 'md'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        return settings

    def createToken(self, info, parent):

        master_page = parent.root.page
        include_page = master_page.findall(info['filename'], maxcount=1)[0]

        #if not include_page.master:
        include_page.master.add(master_page)
        token = IncludeToken(parent, include=include_page)


        #print '\n'
        #print ' MASTER PAGE:', master_page.name, master_page.master
        #print 'INCLUDE PAGE:', include_page.name, include_page.master

        return parent

        """
        #print match

        #print parent.node

        #print self.reader.node, type(self.reader.node), match.groups()

        master_page = parent.root.page
        slave_page = master_page.findall(info['filename'], maxcount=1)[0]
        slave_page.read()

        print '\n'
        print 'MASTER:', master_page
        print ' SLAVE:', slave_page
        #subpage = parent.root.page.
        #subpage.read()

        #TODO: check type of node, must be markdown for this to work or the node needs to be created

        # Set the master node, so that when livereload fires on this included node that the
        # node that does the including is reloaded
        slave_page.master.add(master_page)#subpage.master.add(parent.root.page)
        #print node.name, parent.node.name, node.master

        r =
        self.reader.parse(parent, slave_page)
        ast.page = slave_page
        #for child in ast.children:
        #    child.parent = parent
        return parent
        """

class RenderInclude(components.RenderComponent):
    def createHTML(self, token, parent):
        if token.include.rendered is None:
            token.include.build()#rendered

        #print token.include.rendered

        for child in token.include.rendered:
            child.parent = parent
