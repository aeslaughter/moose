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


class DevelExtension(command.CommandExtension):
    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['preview'] = (True, "Enable/disable the rendered preview.") #TODO: use this
        return config

    def extend(self, reader, renderer):
        self.addCommand(Example())
        self.addCommand(ComponentSettings())

class Example(command.CommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'example'

    TEX_TRANSLATOR = None
    HTML_TRANSLATOR = None

    def __init__(self, *args, **kwargs):
        command.CommandComponent.__init__(self, *args, **kwargs)
        #self.__tex_translator = None
        #self.__html_translator = None

    def init(self, *args, **kwargs):
        command.CommandComponent.init(self, *args, **kwargs)
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
        settings = command.CommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        settings['prefix'] = (u'Example', "The caption prefix (e.g., Example).")
        settings['preview'] = (True, "Display a preview of the rendered result.")
        return settings

    def createToken(self, match, parent):
        #print repr(match['content'])

        master = floats.Float(parent, **self.attributes)
        master.recursive = False

        caption = floats.Caption(master, prefix=self.settings['prefix'], key=self.attributes['id'])

        grammer = self.reader.lexer.grammer('inline')
        self.reader.lexer.tokenize(caption, grammer, unicode(self.settings['caption']), match.line)

        data = match['block'] if 'block' in match else match['inline']

        tabs = floats.Tabs(master)
        tab = floats.Tab(tabs, title=u'MooseDown')
        code = tokens.Code(tab, code=data, language=u'markdown', escape=True)

        # HTML
        ast = tokens.Token(None)
        self.getHTMLTranslator().reader.parse(ast, data)

        root = html.Tag(None, '')
        self.getHTMLTranslator().renderer.process(root, ast)

        code = ''
        for child in root:#.find('body')(0)(0)(0):
            code += child.write()
        if code:
            tab = floats.Tab(tabs, title=u'HTML')
            tokens.Code(tab, code=unicode(code), language=u'HTML', escape=True)

            # PREVIEW
            if self.settings['preview']:
                modal = floats.Modal(caption, title=u"Rendered HTML Preview", icon=u"visibility")
                #content = floats.Content(modal, class_="modal-content")
                ast.parent = modal
                preview = ast

        # LATEX
        """
        #ast = self.getTexTranslator().reader.parse(data)
        tex = self.getTexTranslator().renderer.render(ast)
        code = ''
        for child in tex.find('document'):
            code += child.write()

        if code:
            tab = floats.Tab(tabs, title=u'LaTeX')
            tokens.Code(tab, code=unicode(code), language=u'latex', escape=True)
        """
        return master

class ComponentSettings(command.CommandComponent):
    COMMAND = 'devel'
    SUBCOMMAND = 'settings'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
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

        if hasattr(obj, 'defaultSettings'):
            settings = obj.defaultSettings()
        elif hasattr(obj, 'defaultConfig'):
            settings = obj.defaultConfig()
        else:
            msg = "The '{}' object in the '{}' module does not have a 'defaultSettings' or "\
                  "'defaultConfig' method."
            raise exceptions.TokenizeException(msg, mod, obj)

        rows = [[key, value[0], value[1]] for key, value in settings.iteritems()]

        tbl = table.builder(rows, headings=[u'Key', u'Default', u'Description'])
        tbl.parent = content

        #print master
        return master
