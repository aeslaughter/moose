"""
Extension for adding commands to Markdown syntax.
"""
import re
import uuid
import importlib
import collections

from MooseDocs import common
from MooseDocs.base import components
from MooseDocs.extensions import core, floats
from MooseDocs.tree import html, latex, tokens
from MooseDocs.tree.base import Property

def make_extension():
    return CommandExtension()

class CommandExtension(components.Extension):

    def init(self, translator):
        """
        """
        components.Extension.init(self, translator)

        # Create a location to store the commands. I have tried this a few different ways, but
        # settle on the following, despite its hackishness. First, the commands were stored on the
        # Reader, which I didn't like because I want this extension to be stand-alone. Second, I
        # stored the commands with a static member on this class, but that fails when multiple
        # instances of the translator are created and this method is called again with other
        # instances active. So, my solution is to just sneak the storage into the current translator
        # object.
        if not hasattr(self.translator, '__EXTENSION_COMMANDS__'):
            setattr(self.translator, '__EXTENSION_COMMANDS__', dict())

    def addCommand(self, command):
        """
        Adds a new CommandComponent to the list of available commands.
        """

        # Type checking
        common.check_type('command', command, CommandComponent)
        common.check_type('COMMAND', command.COMMAND, str)
        common.check_type('SUBCOMMAND', command.SUBCOMMAND, (type(None), str, tuple))

        # Initialize the component
        command.init(self.translator)
        command.extension = self

        # Subcommands can be tuples
        if not isinstance(command.SUBCOMMAND, tuple):
            subcommands = tuple([command.SUBCOMMAND])
        else:
            subcommands = command.SUBCOMMAND

        # Add the command and error if it exists
        for sub in subcommands:
            pair = (command.COMMAND, sub)
            if pair in self.translator.__EXTENSION_COMMANDS__:
                msg = "A CommandComponent object exists with the command '{}' and subcommand '{}'."
                raise common.exceptions.MooseDocsException(msg, pair[0], pair[1])
            #elif (command.COMMAND, None) in self.translator.__EXTENSION_COMMANDS__:
            #    msg = "A CommandComponent object exists with the command '{}' with no subcommand, " \
            #          "you can't add a subcommand."
            #    raise common.exceptions.MooseDocsException(msg, command.COMMAND)

            self.translator.__EXTENSION_COMMANDS__[pair] = command

    def extend(self, reader, renderer):
        """
        Adds the various commmand components to the reader.
        """
        reader.addBlock(BlockCommand(), location='_begin')
        reader.addBlock(InlineCommand(), location='<BlockCommand')


class CommandComponent(components.TokenComponent):
    """
    Base component for creating commands.
    """
    COMMAND = None
    SUBCOMMAND = None

class CommandBase(components.TokenComponent):
    """
    Provides a component for creating commands.

    A command is defined by an exclamation mark followed by a keyword and optionally a sub-command.

    This allows all similar patterns to be handled by a single regex, which should aid in parsing
    speed as well as reduce the burden of adding new commands.

    New commands are added by creating a CommandComponent object and adding this component to the
    MarkdownExtension via the addCommand method (see extensions/devel.py for an example).
    """
    PARSE_SETTINGS = False
    FILENAME_RE = re.compile(r'(?P<filename>\S*\.(?P<ext>\w+))', flags=re.UNICODE)

    def __init__(self, *args, **kwargs):
        components.TokenComponent.__init__(self, *args, **kwargs)

    def createToken(self, info, parent):

        cmd = (info['command'], info['subcommand'])
        settings = info['settings']

        # Handle filename and None subcommand
        match = self.FILENAME_RE.search(info['subcommand']) if info['subcommand'] else None
        if match:
            cmd = (info['command'], match.group('ext'))
        elif info['subcommand'] and '=' in info['subcommand']:
            settings += ' ' + info['subcommand']
            cmd = (info['command'], None)

        # Locate the command object to call
        try:
            obj = self.translator.__EXTENSION_COMMANDS__[cmd]
        except KeyError:
            try:
                obj = self.translator.__EXTENSION_COMMANDS__[(cmd[0], '*')]
            except KeyError:
                msg = "The following command combination is unknown: '{} {}'."
                raise common.exceptions.TokenizeException(msg.format(*cmd))

        # Build the token
        settings, _ = common.parse_settings(obj.defaultSettings(), settings)
        obj.setSettings(settings)
        token = obj.createToken(info, parent)
        return token


class InlineCommand(CommandBase):
    RE = re.compile(r'(?:\A|\n{2,})^!(?P<command>\w+)(?: |$)(?P<subcommand>\S+)? *(?P<settings>.*?)(?P<inline>^\S.*?)?(?=\Z|\n{2,})',
                    flags=re.UNICODE|re.MULTILINE|re.DOTALL)

class BlockCommand(CommandBase):
    RE = re.compile(r'(?:\A|\n{2,})^!(?P<command>\w+)!(?: +(?P<subcommand>\w+))? *(?P<settings>.*?)\n+(?P<block>.*?)(^!\1-end!)(?=\Z|\n{2,})',
                    flags=re.UNICODE|re.MULTILINE|re.DOTALL)
