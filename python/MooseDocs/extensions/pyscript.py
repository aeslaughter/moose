#pylint: disable=missing-docstring
import re
from MooseDocs import common
from MooseDocs.common import exceptions
import chigger
from MooseDocs.extensions import command, table, floats
from MooseDocs.tree import tokens


def make_extension(**kwargs):
    return PyScriptExtension(**kwargs)

class PyScriptExtension(command.CommandExtension):
    """
    Enables the direct use of MooseDocs markdown within a python script.
    """

    def extend(self, reader, renderer):
        self.requires(command, table, floats)
        self.addCommand(ChiggerKeybindings())
        self.addCommand(ChiggerOptions())


class ChiggerKeybindings(command.CommandComponent):
    COMMAND = 'chigger'
    SUBCOMMAND = 'keybindings'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the listing content.")
        settings['object'] = (None, "The chigger object to load.")
        settings['prefix'] = (u'Table', "Text to include prior to the included text.")
        return settings

    def createToken(self, info, parent):
        obj = eval(self.settings['object'])()
        rows = []
        for key, bindings in obj.keyBindings().iteritems():
            txt = 'shift-{}'.format(key[0]) if key[1] else key[0]
            for i, binding in enumerate(bindings):
                if i == 0:
                    rows.append((txt, binding.description))
                else:
                    rows.append(('', binding.description))

        tbl = table.builder(rows, headings=['Binding', 'Description'])
        tbl.parent = floats.create_float(parent, self.extension, self.settings, **self.attributes)

        return parent

class ChiggerOptions(command.CommandComponent):
    COMMAND = 'chigger'
    SUBCOMMAND = 'options'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['object'] = (None, "The chigger object to load.")
        return settings

    def createToken(self, info, parent):
        return tokens.String(parent, text='options...')
