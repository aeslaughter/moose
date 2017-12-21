"""
"""
import re
import uuid
import importlib
import collections

from moosedown import base, common
from moosedown.extensions import core, floats
from moosedown.tree import html, latex, tokens
from moosedown.tree.base import Property

def make_extension():
    return IncludeMarkdownExtension(), IncludeRenderExtension()

class IncludeMarkdownExtension(base.MarkdownExtension):

    def extend(self):
        self.addCommand(Include())

class Include(core.MarkdownCommandComponent):
    COMMAND = 'include'
    SUBCOMMAND = 'md'

    @staticmethod
    def defaultSettings():
        settings = core.MarkdownCommandComponent.defaultSettings()
        return settings

    def createToken(self, match, parent):
        node = self.reader.node.findall(match.group('filename'))[0]
        node.read()
        ast = self.translator.ast(node)
        for child in ast:
            child.parent = parent
        return parent

class IncludeRenderExtension(base.RenderExtension):
    def extend(self):
        pass

class RenderInclude(base.RenderComponent):

    def createHTML(self, token, parent):
        raise NotImplementedError("Not done...")

    def createMaterialize(self, token, parent):
        pass
