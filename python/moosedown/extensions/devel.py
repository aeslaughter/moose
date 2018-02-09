"""
Tools primarily for developers of the MooseDown system.
"""
import re
import copy
import uuid
import importlib
import collections

from moosedown import common
from moosedown.common import exceptions
from moosedown.base import components
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

class ExampleToken(tokens.Token):
   PROPERTIES = tokens.Token.PROPERTIES + [Property("data", ptype=unicode, required=True)]


class DevelExtension(command.CommandExtension):
    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['preview'] = (True, "Enable/disable the rendered preview.") #TODO: use this
        return config

    def extend(self, reader, renderer):
        self.addCommand(Example())
        self.addCommand(ComponentSettings())

        renderer.add(ExampleToken, RenderExampleToken())

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

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        settings['prefix'] = (u'Example', "The caption prefix (e.g., Example).")
        return settings

    def createToken(self, match, parent):

        master = floats.Float(parent, **self.attributes)

        caption = floats.Caption(master, prefix=self.settings['prefix'], key=self.attributes['id'])

        grammer = self.reader.lexer.grammer('inline')
        self.reader.lexer.tokenize(caption, grammer, unicode(self.settings['caption']), match.line)

        data = match['block'] if 'block' in match else match['inline']

        example = ExampleToken(master, data=data)

        return example

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

        try:
            mod = importlib.import_module(self.settings['module'])
        except ImportError:
            msg = "Unable to load the '{}' module."
            raise exceptions.TokenizeException(msg, self.settings['module'])

        try:
            obj = getattr(mod, self.settings['object'])
        except AttributeError:
            msg = "Unable to load the '{}' attribute from the '{}' module."
            raise exceptions.TokenizeException(msg, self.settings['object'], self.settings['module'])

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
        return master


class RenderExampleToken(components.RenderComponent):

    def createMaterialize(self, token, parent):

        div = html.Tag(parent, 'div', class_='row card-content')

        # LEFT
        left = html.Tag(div, 'div', class_='moose-example-code col s12 m12 l6')
        ast = tokens.Code(left, code=token.data)
        self.translator.renderer.process(left, ast)

        # RIGHT
        right = html.Tag(div, 'div', class_='moose-example-rendered col s12 m12 l6')
        return right
