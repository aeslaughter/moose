"""
Tools primarily for developers of the MooseDown system.
"""
import re
import uuid

from moosedown import base
from moosedown import tree

def make_extension():
    return DevelMarkdownExtension(), DevelRenderExtension()


class Compare(tree.tokens.Token):
    def __init__(self, parent, markdown=None, html=None):
        super(Compare, self).__init__(parent)
        self.markdown = markdown
        self.html = html

    def __repr__(self):
        return '{}: md={} html={}'.format(self.name, self.markdown, self.html)


class DevelMarkdownExtension(base.MarkdownExtension):
    def extend(self):
        self.addCommand(CodeCompare())

class CodeCompare(base.CommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'moosedown'

    def createToken(self, match, parent):
        content = match.group('content')
        md, html = re.split(r'~{3}', content)
        return Compare(parent, markdown=md, html=html)


class DevelRenderExtension(base.RenderExtension):
    def extend(self):
        self.add(Compare, RenderCompare())

class RenderCompare(base.RenderComponent):

    def createHTML(self, token, parent):
        master = tree.html.Tag('div', parent, class_='moose-code-compare')

        # MooseDown
        md = tree.html.Tag('div', master, class_='moose-code-compare-markdown')
        pre = tree.html.Tag('pre', md)
        code = tree.html.Tag('code', pre)
        tree.html.String(token.markdown, code, escape=True)

        # HTML
        md = tree.html.Tag('div', master, class_='moose-code-compare-html')
        pre = tree.html.Tag('pre', md)
        code = tree.html.Tag('code', pre)
        tree.html.String(token.html, code, escape=True)


    def createMaterialize(self, token, parent):
        master = tree.html.Tag('div', parent, class_='moose-code-compare')
        ul = tree.html.Tag('ul', master, class_="tabs")
        for name, text in [('MooseDown', token.markdown), ('HTML', token.html)]:
            id_ = uuid.uuid4()
            li = tree.html.Tag('li', ul, class_="tab")
            a = tree.html.Tag('a', li, href='#' + str(id_))
            tree.html.String(name, a, escape=True)

            div = tree.html.Tag('div', master, id_=id_)
            pre = tree.html.Tag('pre', div)
            code = tree.html.Tag('code', pre)
            tree.html.String(text, code, escape=True)

        return master
