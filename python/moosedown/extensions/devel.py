"""
Tools primarily for developers of the MooseDown system.
"""
import re
import uuid
import collections

from moosedown import base
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
    PROPERTIES = [Property("tabs", ptype=dict, required=True)]


class DevelMarkdownExtension(base.MarkdownExtension):
    def extend(self):
        self.addCommand(CodeCompare())

class CodeCompare(base.CommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'compare'

    def createToken(self, match, parent):

        tabs = collections.OrderedDict()
        content = match.group('content')
        for match in re.finditer(r'~{3}(?P<title>.*?)$(?P<content>.*?)(?=^~|\Z)', content, flags=re.MULTILINE|re.DOTALL):
            tabs[match.group('title')] = match.group('content')
        return Compare(parent, tabs=tabs)


class DevelRenderExtension(base.RenderExtension):
    def extend(self):
        self.add(Compare, RenderCompare())

class RenderCompare(base.RenderComponent):

    def createHTML(self, token, parent):
        master = tree.html.Tag('div', parent, class_='moose-code-compare')

        for title, code in token.tabs.iteritems():
            div = html.Tag('div', master, class_='moose-code-compare-{}'.format(title))
            pre = html.Tag('pre', div)
            code = html.Tag('code', pre)
            html.String(code, content=code, escape=True)

    def createMaterialize(self, token, parent):
        master = html.Tag('div', parent, class_='moose-code-compare')
        ul = html.Tag('ul', master, class_="tabs")

        for title, content in token.tabs.iteritems():
            id_ = uuid.uuid4()
            li = html.Tag('li', ul, class_="tab")
            a = html.Tag('a', li, href='#' + str(id_))
            html.String(a, content=title, escape=True)

            div = html.Tag('div', master, id_=id_)
            pre = html.Tag('pre', div)
            code = html.Tag('code', pre)
            html.String(code, content=content, escape=True)

        return master

    def createLatex(self, token, parent):
        return latex.Environment(command='UNKNOWN')
