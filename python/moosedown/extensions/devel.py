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


"""TABS extension"""
class Tabs(tokens.Token):
    pass
class Tab(tokens.Token):
    PROPERTIES = [Property("title", ptype=unicode, required=True)]
class TabContent(tokens.Token):
    pass

"""Materialize extension"""
class Row(tokens.Token):
    pass
class Column(tokens.Token):
    pass


class Table(tokens.Token):
    PROPERTIES = [Property('headings', ptype=list), Property('rows', ptype=list)]
    def __init__(self, *args, **kwargs):
        tokens.Token.__init__(self, *args, **kwargs)
        #TODO: error check headings and data

class DevelMarkdownExtension(base.MarkdownExtension):
    def extend(self):
        self.addBlockCommand(Spec())
        self.addCommand(ComponentSettings())

class Spec(core.MarkdownCommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'spec'

    @staticmethod
    def defaultSettings():
        settings = core.MarkdownCommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        #settings['class'] = ('moose-devel-code-compare', settings['class'][1])
        return settings

    def createToken(self, match, parent):
        example = tokens.Float(parent, label="example", caption=self.settings['caption'], **self.attributes )
        tabs = Tabs(example)

        #print match.group('content')
        content = match.group('content').split('~~~')
        #print repr(content)

        md = Tab(tabs, title=u'MooseDown')
        tokens.Code(TabContent(md), code=content[0], language=u'markdown')

        html = Tab(tabs, title=u'HTML')
        tokens.Code(TabContent(html), code=content[1], language=u'html')

        rendered = Tab(tabs, title=u'HTML (Rendered)')
        root = TabContent(rendered, class_="moose-html-rendered-tab")
        root = self.reader.parse(content[0], root)

        tex = Tab(tabs, title=u'Latex')
        tokens.Code(TabContent(tex), code=content[2], language=u'latex')


        """
        # TODO: this is for tabs
        #regex = r'~{3}(?P<title>.*?)(?:\s+(?P<settings>.*?))?$(?P<content>.*?)(?=^~|\Z)'

        for i, match in enumerate(re.finditer(regex, content, flags=re.MULTILINE|re.DOTALL)):
            settings, _ = common.parse_settings(defaults, match.group('settings'))
            #id_ = uuid.uuid4()

            if i == 0:
                tab = Tab(left, title=match.group('title'))
            else:
                tab = Tab(right, title=match.group('title'))

            content = TabContent(tab)
            code = tokens.Code(content, code=match.group('content'), language=settings['language'])
        """
        return example

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
        if self.settings['module'] is None:
            raise base.TokenizeException()
        #TODO: error if 'module' and 'object' not provided
        #TODO: this should raise, but result in an error token

        mod = importlib.import_module(self.settings['module'])
        obj = getattr(mod, self.settings['object'])

        #TODO: error if defaultSettings not there or  it returns something that is not a dict()
        settings = obj.defaultSettings()
        rows = [[key, value[0], value[1]] for key, value in settings.iteritems()]
        return Table(parent, headings=[u'Key', u'Default', u'Description'], rows=rows)


class DevelRenderExtension(base.RenderExtension):
    def extend(self):

        self.add(Row, RenderRow())
        self.add(Column, RenderColumn())

        self.add(Tabs, RenderTabs())
        self.add(Tab, RenderTab())
        self.add(TabContent, RenderTabContent())

        self.add(tokens.Float, RenderFloat())

        self.add(Table, RenderTable())

class RenderFloat(base.RenderComponent):
    def __init__(self, *args, **kwargs):
        base.RenderComponent.__init__(self, *args, **kwargs)
        self._count = collections.defaultdict(int)

    def reinit(self):
        self._count.clear()

    def createHTML(self, token, parent):
        attrs = token.attributes
        if attrs['class'] is not None:
            attrs['class'] = 'moose-float-div'
        div = html.Tag(parent, 'div', **attrs)

        if token.caption:
            self._count[token.label] += 1
            caption = html.Tag(div, 'p', class_="moose-float-caption")
            heading = html.Tag(caption, 'span', class_="moose-float-caption-heading")
            html.String(heading, content=u'{} {}: '.format(token.label.title(), self._count[token.label]))
            text = html.Tag(caption, 'span', class_="moose-float-caption-text")
            html.String(text, content=token.caption)

        return div

class RenderRow(base.RenderComponent):
    def createHTML(self, token, parent):
        return html.Tag(parent, 'div', class_="row")#, **token.attributes)

class RenderColumn(base.RenderComponent):
    def createHTML(self, token, parent):
        return html.Tag(parent, 'div', class_="col s12 m12 l4")#, **token.attributes)

class RenderTabs(base.RenderComponent):

    def createHTML(self, token, parent):
        #row = html.Tag(parent, 'div', class_="row", **token.attributes)
        #col = html.Tag(row, 'div', class_="col s12 m6")
        return html.Tag(parent, 'ul', class_="tabs")

#    def createMaterialize(self, token, parent):
#        return self.createHTML(token, parent)
        #for child in token:
        #    li = html.Tag(ul, 'li', class_="tab")
        #    a = html.Tag(li, 'a', href='#' + str(child['id']))
        #    html.String(a, content=child.title, escape=True)

    def createLatex(self, token, parent):
        pass
        #TODO: do something
        #return latex.Environment(parent, 'UNKNOWN')

class RenderTab(base.RenderComponent):
    def createHTML(self, token, parent):
        li = html.Tag(parent, 'li', class_="tab")
        a = html.Tag(li, 'a', href='#{}'.format(uuid.uuid4()))
        html.String(a, content=token.title)
        return li

    #def createMaterialize(self, token, parent):
    #    return self.createHTML(token, parent)

class RenderTabContent(base.RenderComponent):
    def createHTML(self, token, parent):
        a = parent.find('a')
        return html.Tag(parent.parent.parent, 'div', id_=a['href'].strip('#'), **token.attributes)

    #def createMaterialize(self, token, parent):
    #    return self.createHTML(token, parent)


class RenderTable(base.RenderComponent):

    #def createMaterialize(self, token, parent):
    #    return self.createHTML(token, parent)

    def createHTML(self, token, parent):
        attrs = token.attributes
        attrs['class'] = 'moose-table-div'
        tbl = html.Tag(parent, 'table', **attrs)
        tr = html.Tag(tbl, 'tr')
        for h in token.headings:
            th = html.Tag(tr, 'th')
            html.String(th, content=unicode(h), escape=True)
        for r in token.rows:
            tr = html.Tag(tbl, 'tr')
            for d in r:
                td = html.Tag(tr, 'td')
                html.String(td, content=unicode(d), escape=True)
        return tbl
