"""
Tools primarily for developers of the MooseDown system.
"""
import re
import copy
import uuid
import importlib
import collections

from moosedown import base, common
from moosedown.extensions import core, floats, command, table
from moosedown.tree import html, latex, tokens
from moosedown.tree.base import Property

def make_extension():
    return DevelExtension()

"""
class Example(tokens.Token):
    PROPERTIES = [Property("caption", ptype=unicode, required=True),
                 # Property("prefix", ptype=unicode, default=u'Example'),
                  Property("data", ptype=collections.OrderedDict, required=True),
                  Property("preview")]
"""


class DevelExtension(base.Extension):
    #TODO: require float, commands

    def extend(self, reader, renderer):
        reader.addCommand(Example())
        reader.addCommand(ComponentSettings())

class Example(command.MarkdownCommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'example'
    #EXAMPLE_RE = re.compile(r'^~~~ *(?P<settings>.*?)$(?P<content>.*?)(?=^~~~|\Z)',
    #                        flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    TEX_TRANSLATOR = None
    HTML_TRANSLATOR = None

    def __init__(self, *args, **kwargs):
        command.MarkdownCommandComponent.__init__(self, *args, **kwargs)
        #self.__tex_translator = None
        #self.__html_translator = None

    def init(self, *args, **kwargs):
        command.MarkdownCommandComponent.init(self, *args, **kwargs)
        self.__counts = collections.defaultdict(int)
        # TODO: check current type
        #self.__html_renderer = base.MaterializeRenderer()

        #self.__html_translator = base.Translator(type(self.reader)(), base.MaterializeRenderer(), copy.deepcopy(self.translator.extensions))
        #self.__tex_translator = base.Translator(type(self.reader)(), base.LatexRenderer(), self.translator.extensions)

    def getTexTranslator(self):
        if self.TEX_TRANSLATOR is None:
            extensions = [type(ext)(**ext.getConfig()) for ext in self.translator.extensions]
            self.TEX_TRANSLATOR = base.Translator(type(self.reader)(), base.LatexRenderer(), extensions)
        return self.TEX_TRANSLATOR

    def getHTMLTranslator(self):
        if self.HTML_TRANSLATOR is None:
            extensions = [type(ext)(**ext.getConfig()) for ext in self.translator.extensions]
            self.HTML_TRANSLATOR = base.Translator(type(self.reader)(), base.MaterializeRenderer(), extensions)
        return self.HTML_TRANSLATOR


    @staticmethod
    def defaultSettings():
        settings = command.MarkdownCommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        settings['prefix'] = (u'Example', "The caption prefix (e.g., Example).")
        settings['preview'] = (True, "Display a preview of the rendered result.")
        return settings

    def createToken(self, match, parent):


        master = floats.Float(parent, **self.attributes)
        caption = floats.Caption(master, prefix=self.settings['prefix'], key=self.attributes['id'])

        grammer = self.reader.lexer.grammer('inline')
        self.reader.lexer.tokenize(caption, grammer, unicode(self.settings['caption']), match.line)

        data = match['content']

        tabs = floats.Tabs(master)
        tab = floats.Tab(tabs, title=u'MooseDown')
        tokens.Code(tab, code=data, language=u'markdown', escape=True)

        # HTML
        ast = tokens.Token(None)
        self.getHTMLTranslator().reader.parse(ast, data)

        root = html.Tag(None, '')
        self.getHTMLTranslator().renderer.process(ast, root)

        code = ''
        for child in root:#.find('body')(0)(0)(0):
            code += child.write()
        if code:
            tab = floats.Tab(tabs, title=u'HTML')
            tokens.Code(tab, code=unicode(code), language=u'HTML', escape=True)

            # PREVIEW
            if self.settings['preview']:
                modal = floats.Modal(caption, title=u"HTML Preview", icon=u"visibility")
                #content = floats.Content(modal, class_="modal-content")
                ast.parent = modal
                preview = ast

        # LATEX
        #ast = self.getTexTranslator().reader.parse(data)
        tex = self.getTexTranslator().renderer.render(ast)
        code = ''
        for child in tex.find('document'):
            code += child.write()

        if code:
            tab = floats.Tab(tabs, title=u'LaTeX')
            tokens.Code(tab, code=unicode(code), language=u'latex', escape=True)


        return master

class ComponentSettings(command.MarkdownCommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'settings'

    @staticmethod
    def defaultSettings():
        settings = command.MarkdownCommandComponent.defaultSettings()
        settings['module'] = (None, "The name of the module containing the object.")
        settings['object'] = (None, "The name of the object to import from the 'module'.")
        settings['caption'] = (None, "The caption to use for the settings table created.")
        settings['prefix'] = (u'Table', "The caption prefix (e.g., Table).")

        return settings

    def createToken(self, match, parent):
        if self.settings['module'] is None:
            raise base.TokenizeException()
        #TODO: error if 'module' and 'object' not provided
        #TODO: this should raise, but result in an error token

        master = floats.Float(parent, **self.attributes)

        if self.settings['caption']:
            caption = floats.Caption(master, prefix=self.settings['prefix'], key=self.attributes['id'])
            grammer = self.reader.lexer.grammer('inline')
            self.reader.lexer.tokenize(caption, grammer, self.settings['caption'], match.line)#, line=self.line)

        content = floats.Content(master, class_="card-content")

        mod = importlib.import_module(self.settings['module'])
        obj = getattr(mod, self.settings['object'])

        #TODO: error if defaultSettings not there or  it returns something that is not a dict()
        settings = obj.defaultSettings()
        rows = [[key, value[0], value[1]] for key, value in settings.iteritems()]

        tbl = table.builder(rows, headings=[u'Key', u'Default', u'Description'])
        tbl.parent = content

        #print master
        return master


#class DevelRenderExtension(base.RenderExtension):
#    def extend(self):
#        pass
        #self.add(Example, RenderExample())
        #self.add(Table, RenderTable())

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
            html.String(btn, content=u'HTML Preview')
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
