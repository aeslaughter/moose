import re

from moosedown import common
from moosedown.base import components
from moosedown.extensions import core
from moosedown.tree import html, latex, tokens
from moosedown.tree.base import Property

#from moosedown.extensions import floats

def make_extension(**kwargs):
    return TableExtension(**kwargs)

#class Table(object):
#    def __init__


class TableToken(tokens.Token):
    PROPERTIES = [Property('headings', ptype=list),
                  Property('rows', required=True, ptype=list),
                  Property('format', ptype=list)]
    def __init__(self, *args, **kwargs):
        tokens.Token.__init__(self, *args, **kwargs)
        #TODO: error check headings, data, and format

        if self.format is None:
            self.format = [self.LEFT] * len(self.rows[0])


class Table(tokens.Token):
    pass

class TableBody(tokens.Token):
    pass

class TableHead(tokens.Token):
    pass

class TableRow(tokens.Token):
    pass

class TableItem(tokens.Token):
    PROPERTIES = [Property('align', ptype=str, default='center')]

class TableHeaderItem(TableItem):
    pass

def builder(rows, headings=None):
    node = Table()
    if headings:
        thead = TableHead(node)
        row = TableRow(thead)
        for h in headings:
            th = TableHeaderItem(row)
            tokens.String(th, content=unicode(h))

    tbody = TableBody(node)
    for data in rows:
        row = TableRow(tbody)
        for d in data:
            tr = TableItem(row)
            tokens.String(tr, content=unicode(d))

    return node

class TableExtension(components.Extension): #TODO:  CommandMarkdownExtension
    def extend(self, reader, renderer):
        #reader.addBlock(TableComponent(), "<moosedown.extensions.core.Paragraph")
        reader.addBlock(TableComponent(), "<Paragraph")

        #print 'TableExtension::extend' #TODO: The devel Example extension calls this way too many times...
        renderer.add(Table, RenderTable())
        renderer.add(TableHead, RenderTag('thead'))
        renderer.add(TableBody, RenderTag('tbody'))
        renderer.add(TableRow, RenderTag('tr'))
        renderer.add(TableHeaderItem, RenderTag('th'))
        renderer.add(TableItem, RenderTag('td'))


class TableComponent(components.TokenComponent):
    RE = re.compile(r'(?:\A|\n{2,})^(?P<table>\|.*?)(?=\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL|re.UNICODE)
    FORMAT_RE = re.compile(r'^(?P<format>\|[ \|:\-]+\|)$', flags=re.MULTILINE|re.UNICODE)

    def createToken(self, match, parent):


        grammer = self.reader.lexer.grammer('inline')


        content = match['table']
        table = Table(parent)



        head = None
        body = None
        form = None

        format_match = self.FORMAT_RE.search(content)
        if format_match:
            head = [item.strip() for item in content[:format_match.start('format')-1].split('|') if item]
            body = content[format_match.end('format'):]
            form = [item.strip() for item in format_match.group('format').split('|') if item]

        if form:
            for i, string in enumerate(form):
                if string.startswith(':'):
                    form[i] = 'left'
                elif string.endswith(':'):
                    form[i] = 'right'
                elif string.startswith('-'):
                    form[i] = 'center'
                else:
                    # TODO: warning/error
                    form[i] = 'left'
                #print string, form[i]

        if head:

            row = TableRow(TableHead(table))
            for i, h in enumerate(head):
                item = TableHeaderItem(row, format=form[i])
                self.reader.lexer.tokenize(item, grammer, h, match.line) #TODO: add line number


        for line in body.splitlines():
            if line:
                row = TableRow(TableBody(table))
                for i, content in enumerate([item.strip() for item in line.split('|') if item]):
                    item = TableItem(row, format=form[i])
                    self.reader.lexer.tokenize(item, grammer, content, match.line) #TODO: add line number



        return table





class RenderTable(components.RenderComponent):
    def createHTML(self, token, parent):
        attrs = token.attributes
        attrs['class'] = 'moose-table-div'
        div = html.Tag(parent, 'div', **attrs)
        tbl = html.Tag(div, 'table')
        return tbl
    def createMaterialize(self, token, parent):
        return self.createHTML(token, parent)
    def createLatex(self, token, parent):
        pass

class RenderTag(components.RenderComponent):
    def __init__(self, tag):
        components.RenderComponent.__init__(self)
        self.__tag = tag

    def createMaterialize(self, token, parent):
        return self.createHTML(token, parent)

    def createHTML(self, token, parent):
        return html.Tag(parent, self.__tag)

    def createLatex(self, token, parent):
        pass

"""
class RenderTableSection(components.RenderComponent):
    def __init__(self, tag_name):
        components.RenderComponent.__init__(self)
        self.__tag_name = tag_name
"""


#class RenderTableRow(components.RenderComponent):
#    def createHTML(self, token, parent):
#        return html.Tag('')

"""
class RenderTable(components.RenderComponent):
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
"""
