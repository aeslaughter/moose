import re

from moosedown import base, common
from moosedown.extensions import core
from moosedown.tree import html, latex, tokens
from moosedown.tree.base import Property

#from moosedown.extensions import floats

def make_extension():
    return TableMarkdownExtension(), TableRenderExtension()



class Table(tokens.Token):
    PROPERTIES = [Property('headings', ptype=list),
                  Property('rows', required=True, ptype=list),
                  Property('format', ptype=list)]
    CENTER = 0
    LEFT = 1
    RIGHT = 2

    def __init__(self, *args, **kwargs):
        tokens.Token.__init__(self, *args, **kwargs)
        #TODO: error check headings, data, and format

        if self.format is None:
            self.format = [self.LEFT] * len(self.rows[0])




class TableMarkdownExtension(base.MarkdownExtension): #TODO:  CommandMarkdownExtension
    def extend(self):
        self.addBlock(TableComponent(), "<moosedown.extensions.core.Paragraph")

class TableRenderExtension(base.RenderExtension):
    def extend(self):
        self.add(Table, RenderTable())


class TableComponent(core.MarkdownComponent):
    RE = re.compile(r'^(?P<table>\|.*?^[^\|])', flags=re.MULTILINE|re.DOTALL|re.UNICODE)
    FORMAT_RE = re.compile(r'^(?P<format>\|[ \|:\-]+\|)$', flags=re.MULTILINE|re.UNICODE)

    def createToken(self, match, parent):
        content = match.group('table')

        head = None
        body = None
        form = None

        format_match = self.FORMAT_RE.search(content)
        if format_match:
            head = [item.strip() for item in content[:format_match.start('format')-1].split('|') if item]
            body = content[format_match.end('format'):]
            form = [item.strip() for item in format_match.group('format').split('|') if item]

        rows = []
        if not body:
            #TODO: error
            pass

        for line in body.splitlines():
            if line:
                rows.append([item.strip() for item in line.split('|') if item])


        if form:
            for i, string in enumerate(form):
                if string.startswith(':'):
                    form[i] = Table.LEFT
                elif string.endswith(':'):
                    form[i] = Table.RIGHT
                elif string.startswith('-'):
                    form[i] = Table.CENTER
                else:
                    # TODO: warning/errorg
                    form[i] = Table.LEFT
                print string, form[i]

        return Table(parent, rows=rows, headings=head, format=form)
        #lines = .splitlines()



class RenderTable(base.RenderComponent):
    ALIGN = {Table.CENTER:u'center', Table.LEFT:u'left', Table.RIGHT:u'right'}

    def createHTML(self, token, parent):
        attrs = token.attributes
        attrs['class'] = 'moose-table-div'
        div = html.Tag(parent, 'div', **attrs)
        tbl = html.Tag(div, 'table')

        if token.headings:
            thead = html.Tag(tbl, 'thead')
            tr = html.Tag(thead, 'tr')
            for i, h in enumerate(token.headings):
                th = html.Tag(tr, 'th')
                th.style['text-align'] = self.ALIGN[token.format[i]]
                html.String(th, content=unicode(h), escape=True)

        tbody = html.Tag(tbl, 'tbody')
        for r in token.rows:
            tr = html.Tag(tbody, 'tr')
            for i, d in enumerate(r):
                td = html.Tag(tr, 'td')
                td.style['text-align'] = self.ALIGN[token.format[i]]
                html.String(td, content=unicode(d), escape=True)
        return div
