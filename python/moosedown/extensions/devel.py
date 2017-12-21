"""
Tools primarily for developers of the MooseDown system.
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
    return DevelMarkdownExtension(), DevelRenderExtension()

"""
class Example(tokens.Token):
    PROPERTIES = [Property("caption", ptype=unicode, required=True),
                 # Property("prefix", ptype=unicode, default=u'Example'),
                  Property("data", ptype=collections.OrderedDict, required=True),
                  Property("preview")]
"""

class Table(tokens.Token):
    PROPERTIES = [Property('headings', ptype=list), Property('rows', ptype=list)]
    def __init__(self, *args, **kwargs):
        tokens.Token.__init__(self, *args, **kwargs)
        #TODO: error check headings and data

class DevelMarkdownExtension(base.MarkdownExtension):
    #TODO: require float, materializes

    def extend(self):
        self.addCommand(Example())
        self.addCommand(ComponentSettings())

class Example(core.MarkdownCommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'example'
    EXAMPLE_RE = re.compile(r'^~~~ *(?P<settings>.*?)$(?P<content>.*?)(?=^~~~|\Z)',
                            flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    @staticmethod
    def defaultSettings():
        settings = core.MarkdownCommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        settings['prefix'] = (u'Example', "The caption prefix (e.g., Example).")
        settings['preview'] = (True, "Display a preview of the rendered result.")
        #settings['class'] = ('moose-devel-code-compare', settings['class'][1])
        return settings

    def createToken(self, match, parent):
        master = floats.Float(parent)
        caption = floats.Caption(master, prefix=u'Example')

        grammer = self.reader.lexer.grammer('inline')
        self.reader.lexer.tokenize(self.settings['caption'], caption, grammer)#, line=self.line)

        data = match.group('content').split('~~~')[1:]

        tabs = floats.Tabs(master)
        tab = floats.Tab(tabs, title=u'MooseDown')
        tokens.Code(tab, code=data[0], language=u'markdown', escape=True)

        tab = floats.Tab(tabs, title=u'HTML')
        tokens.Code(tab, code=data[1], language=u'HTML', escape=True)

        tab = floats.Tab(tabs, title=u'LaTeX')
        tokens.Code(tab, code=data[2], language=u'latex', escape=True)

        if self.settings['preview']:
            modal = floats.Modal(caption, title=u"Preview", icon=u"visibility")
            #content = floats.Content(modal, class_="modal-content")
            preview = self.reader.parse(data[0], modal)

        return master

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
        #self.add(Example, RenderExample())
        self.add(Table, RenderTable())

class RenderExample(base.RenderComponent):
    def __init__(self, *args, **kwargs):
        base.RenderComponent.__init__(self, *args, **kwargs)
        self._count = 0

    def reinit(self):
        self._count = 0

    def createHTML(self, token, parent):
        raise NotImplementedError("Not done...")

    def createMaterialize(self, token, parent):

        self._count += 1
        prefix = u'Example {}: '.format(self._count)

        row = html.Tag(parent, 'div', class_="row")
        col = html.Tag(row, 'div', class_="col s12")
        card = html.Tag(col, 'div', class_="card")
        cap_div = html.Tag(card, 'div', class_="card-content")
        obj = common.float.Caption(u"Example", self._count, token.caption)
        obj.createMaterialize()
        caption = html.Tag(cap_div, 'p', class_="moose-caption")
        heading = html.Tag(caption, 'span', class_="moose-caption-heading")
        html.String(heading, content=prefix)
        text = html.Tag(caption, 'span', class_="moose-caption-text")
        html.String(text, content=token.caption)

        tabs = html.Tag(card, 'div', class_="card-tabs")
        ul = html.Tag(tabs, 'ul', class_="tabs")
        tab_content = html.Tag(card, 'div', class_='card-content grey lighten-4')

        for key, value in token.data.iteritems():
            id_ = uuid.uuid4()
            li = html.Tag(ul, 'li', class_="tab")
            tab = html.Tag(li, 'a', class_="active", href="#{}".format(id_))
            html.String(tab, content=key)

            div = html.Tag(tab_content, 'div', id=id_)
            pre = html.Tag(div, 'pre')
            code = html.Tag(pre, 'code', class_="language-{}".format(key.lower()))
            html.String(code, content=value, escape=True)

        # Preview
        if token.preview:
            tag = uuid.uuid4()
            btn = html.Tag(caption, 'a', class_="btn modal-trigger right", href="#{}".format(tag) )
            icon = html.Tag(btn, 'i', class_="material-icons right")
            html.String(btn, content=u'Preview')
            html.String(icon, content=u"visibility")

            modal = html.Tag(parent, 'div', class_="modal", id_=tag)
            modal_content = html.Tag(modal, 'div', class_="modal-content")
            #heading = html.Tag(modal_content, 'h4')
            #html.Tag(heading)

            preview = self.renderer.render(token.preview, reinit=False)
            preview.find('body').parent = modal_content

            footer = html.Tag(modal, 'div', class_="modal-footer grey lighten-3")
            close = html.Tag(footer, 'a', class_="modal-action modal-close btn-flat")
            html.String(close, content=u'Done')



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
