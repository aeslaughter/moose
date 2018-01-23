"""
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
    return CommandExtension()

class CommandExtension(base.Extension):

    # A common storage for all command objects, based on the COMMAND/SUBCOMMAND tuple
    __COMMANDS__ = dict()

    def addCommand(self, command):
        """
        Adds a new CommandComponent to the list of available commands.
        """
        if not isinstance(command, CommandComponent):
            msg = "Expected a {} object but a {} was provided."
            raise common.exceptions.MooseDocsException(msg, CommandComponent, type(command))

        pair = (command.COMMAND, command.SUBCOMMAND)
        if pair in CommandExtension.__COMMANDS__:
            msg = "A CommandComponent object exists with the command '{}' and subcommand '{}'."
            raise common.exceptions.MooseDocsException(msg, pair[0], pair[1])

        self.__COMMANDS__[pair] = command

    def extend(self, reader, renderer):
        """
        Adds the various commmand components to the reader.
        """
        reader.addBlock(FileCommand(), location='_begin')
        reader.addBlock(InlineCommand(), location='_begin')
        reader.addBlock(BlockCommand(), location='_begin')

class CommandComponent(base.TokenComponent):
    """
    Base component for creating commands.
    """
    COMMAND = None
    SUBCOMMAND = None

class CommandBase(base.TokenComponent):
    """
    Provides a component for creating commands.

    A command is defined by an exclamation mark followed by a keyword and optionally a sub-command.

    This allows all similar patterns to be handled by a single regex, which should aid in parsing
    speed as well as reduce the burden of adding new commands.

    New commands are added by creating a CommandComponent object and adding this component to the
    MarkdownExtension via the addCommand method (see extensions/devel.py for an example).
    """
    PARSE_SETTINGS = False
    def __init__(self, *args, **kwargs):
        core.MarkdownComponent.__init__(self, *args, **kwargs)
        #self.__commands = dict()#base.MarkdownReader.__COMMANDS__ #TODO: this should be the storage, CommandExtension should add the addCommand method

    def createToken(self, info, parent):
        #print 'CommandBase:', match.groups()
        cmd = (match['command'], match['subcommand'])

        #TODO: Error check
        if cmd not in CommandExtension.__COMMANDS__:
            msg = "The following command combination is unknown: '{} {}'."
            raise common.exceptions.TokenizeException(msg.format(*cmd))

        obj = CommandExtension.__COMMANDS__[cmd]
        obj.settings, _ = common.parse_settings(obj.defaultSettings(), match['settings'])
        if obj.translator is None:
            obj.init(self.translator)
        token = obj.createToken(info, parent)
        return token

    """
    def setup(self, value):
        MarkdownComponent.setup(self, value)
        for obj in self.COMMANDS.itervalues():
            obj.setup(value)
    """

class InlineCommand(CommandBase):
    RE = re.compile(r'(?:\A|\n{2,})^!(?P<command>\w+) *(?P<subcommand>\w+)? *(?P<settings>.*?)(?=\Z|\n{2,})',
                    flags=re.UNICODE|re.MULTILINE)

class BlockCommand(CommandBase):
    RE = re.compile(r'(?:\A|\n{2,})^!(?P<command>\w+)! *(?P<subcommand>\w+)? *(?P<settings>.*?)\n+(?P<content>.*?)(^!\1-end!)(?=\Z|\n{2,})',
                    flags=re.UNICODE|re.MULTILINE|re.DOTALL)

class FileCommand(CommandBase):
    RE = re.compile(r'(?:\A|\n{2,})^!(?P<command>\w+) (?P<filename>\S*?\.(?P<subcommand>\w+)) *(?P<settings>.*?)(?=\Z|\n{2,})',
                    flags=re.UNICODE|re.MULTILINE|re.DOTALL)
