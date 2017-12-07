"""
Tools primarily for developers of the MooseDown system.
"""
import re
import uuid
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
        tabs: Dict of code tabs to dislpay.
    """
    pass #PROPERTIES = [Property("tabs", ptype=dict, required=True)]

class CompareCode(tokens.Code):
    PROPERTIES = tokens.Code.PROPERTIES + [Property("title", ptype=unicode, required=True)]


class DevelMarkdownExtension(base.MarkdownExtension):
    def extend(self):
        self.addCommand(CodeCompare())

class CodeCompare(base.CommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'compare'

    def createToken(self, match, parent):
        compare = Compare(parent)

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


class DevelRenderExtension(base.RenderExtension):
    def extend(self):
        self.add(Compare, RenderCompare())

class RenderCompare(base.RenderComponent):

    def createHTML(self, token, parent):
        master = tree.html.Tag('div', parent, class_='moose-code-compare')

        """
        for title, code in token.tabs.iteritems():
            div = html.Tag(master, 'div', class_='moose-code-compare-{}'.format(title))
            pre = html.Tag(div, 'pre')
            code = html.Tag(pre, 'code')
            html.String(code, content=code, escape=True)
        """
        return master

    def createMaterialize(self, token, parent):
        master = html.Tag(parent, 'div', class_='moose-code-compare')
        ul = html.Tag(master, 'ul', class_="tabs")

        for child in token:
            li = html.Tag(ul, 'li', class_="tab")
            a = html.Tag(li, 'a', href='#' + str(child['id']))
            html.String(a, content=child.title, escape=True)

        return master

    def createLatex(self, token, parent):
        pass
        #return latex.Environment(parent, 'UNKNOWN')
