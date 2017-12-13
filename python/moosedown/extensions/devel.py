"""
Tools primarily for developers of the MooseDown system.
"""
import re
import uuid
import importlib
import collections

from moosedown import base, common
from moosedown.extensions import core
from moosedown.tree import html, latex, tokens
from moosedown.tree.base import Property

def make_extension():
    return DevelMarkdownExtension(), DevelRenderExtension()


class Compare(tokens.Token):
    """
    Tool for comparing code, i.e. html, latex, etc.

    Inputs:
        tabs: Dict of code tabs to display.
    """
    pass #PROPERTIES = [Property("tabs", ptype=dict, required=True)]

class CompareCode(tokens.Code):
    PROPERTIES = tokens.Code.PROPERTIES + [Property("title", ptype=unicode, required=True)]

class TokenSettings(tokens.Token):
    PROPERTIES = [Property('settings', ptype=dict, required=True)]

class DevelMarkdownExtension(base.MarkdownExtension):
    def extend(self):
        self.addCommand(CodeCompare())
        self.addCommand(ComponentSettings())

class CodeCompare(core.MarkdownCommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'compare'

    def createToken(self, match, parent):
        compare = Compare(parent, **self.attributes)

        #tabs = collections.OrderedDict()
        content = match.group('content')
        regex = r'~{3}(?P<title>.*?)(?:\s+(?P<settings>.*?))?$(?P<content>.*?)(?=^~|\Z)'

        #TODO: handle settings from Code
        defaults = core.Code.defaultSettings()
        for match in re.finditer(regex, content, flags=re.MULTILINE|re.DOTALL):
            settings, _ = common.parse_settings(defaults, match.group('settings'))

            #TODO: error if id set or unknown
            CompareCode(compare, title=match.group('title'), code=match.group('content'),
                        id_=uuid.uuid4(), language=settings['language'])
        return compare

class ComponentSettings(core.MarkdownCommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'settings'

    @staticmethod
    def defaultSettings():
        settings = core.MarkdownCommandComponent.defaultSettings()
        settings['module'] = (None, "The name of the module containing the object.")
        settings['object'] = (None, "The name of the object to import from the 'module'.")
        return settings

    def createToken(self, match, parent):
        #print match.groups()

        #TODO: error if 'module' and 'object' not provided
        #TODO: this should raise, but result in an error token

        mod = importlib.import_module(self.settings['module'])
        obj = getattr(mod, self.settings['object'])
        return TokenSettings(settings=obj.defaultSettings()) #TODO: error if defaultSettings not there or  it returns something that is not a dict()


class DevelRenderExtension(base.RenderExtension):
    def extend(self):
        self.add(Compare, RenderCompare())

class RenderCompare(base.RenderComponent):

    def createHTML(self, token, parent):
        master = tree.html.Tag('div', parent, class_='moose-code-compare', **token.attributes)
        return master

    def createMaterialize(self, token, parent):
        master = html.Tag(parent, 'div', class_='moose-code-compare', **token.attributes)
        ul = html.Tag(master, 'ul', class_="tabs")

        for child in token:
            li = html.Tag(ul, 'li', class_="tab")
            a = html.Tag(li, 'a', href='#' + str(child['id']))
            html.String(a, content=child.title, escape=True)

        return master

    def createLatex(self, token, parent):
        pass
        #return latex.Environment(parent, 'UNKNOWN')
