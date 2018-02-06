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

        return parent

class RenderInclude(components.RenderComponent):
    def createHTML(self, token, parent):
        if token.include.rendered is None:
            token.include.build()

        for child in token.include.rendered:
            child.parent = parent
