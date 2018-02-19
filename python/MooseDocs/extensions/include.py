"""
"""
import re
import uuid
import importlib
import collections
import copy

from MooseDocs import common
from MooseDocs.base import components
from MooseDocs.extensions import core, command, floats
from MooseDocs.tree import html, latex, tokens, page
from MooseDocs.tree.base import Property

class IncludeToken(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + \
                 [Property("include", ptype=page.MarkdownNode, required=True)]

def make_extension(**kwargs):
    return IncludeExtension()

class IncludeExtension(command.CommandExtension):

    def extend(self, reader, renderer):
        self.requires(command)

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
        include_page = master_page.findall(info['subcommand'], maxcount=1)[0]

        #if not include_page.master:
        include_page.master.add(master_page)
        token = IncludeToken(parent, include=include_page)

        return parent

class RenderInclude(components.RenderComponent):

    def create(self, token, parent):
        ast = token.include.ast()
        for child in ast:
            self.translator.renderer.process(parent, child)

    def createHTML(self, token, parent):
        return self.create(token, parent)

    def createLatex(self, token, parent):
        return self.create(token, parent)
