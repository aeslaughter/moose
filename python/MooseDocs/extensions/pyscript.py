#pylint: disable=missing-docstring
import re
from MooseDocs import common
from MooseDocs.common import exceptions
from MooseDocs.extensions import command
from MooseDocs.tree import tokens


def make_extension(**kwargs):
    return PyScriptExtension(**kwargs)

class PyScriptExtension(command.CommandExtension):
    """
    Enables the direct use of MooseDocs markdown within a python script.
    """

    def extend(self, reader, renderer):
        self.requires(command)
        self.addCommand(ChiggerKeybindings())
        self.addCommand(ChiggerOptions())


class ChiggerKeybindings(command.CommandComponent):
    COMMAND = 'chigger'
    SUBCOMMAND = 'keybindings'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['object'] = (None, "The chigger object to load.")
        return settings

    def createToken(self, info, parent):
        print self.settings
        return tokens.String('keybindings...')

class ChiggerOptions(command.CommandComponent):
    COMMAND = 'chigger'
    SUBCOMMAND = 'options'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['object'] = (None, "The chigger object to load.")
        return settings

    def createToken(self, info, parent):
        print self.settings
        return tokens.String('options...')
