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
    return CommandMarkdownExtension(), CommandRenderExtension()

class CommandMarkdownExtension(base.MarkdownExtension):

    def extend(self):
        self.addBlock(FileCommand(), location='<moosedown.extensions.core.Code')
        self.addBlock(InlineCommand(), location='>moosedown.extensions.command.FileCommand')
        self.addBlock(BlockCommand(), location='>moosedown.extensions.command.InlineCommand')


#        self.addCommand(Include())

class MarkdownCommandComponent(base.TokenComponent):
    """
    Base Markdown component for creating commands.
    """
    COMMAND = None
    SUBCOMMAND = None


    @staticmethod
    def defaultSettings():
        return base.TokenComponent.defaultSettings()

    @property
    def attributes(self):
        """
        Return a dictionary with the common html settings.
        """
        return {'style':self.settings['style'], 'id':self.settings['id'], 'class':self.settings['class']}

class CommandBase(core.MarkdownComponent):
    """
    Provides a component for creating commands.

    A command is defined by an exclamation mark followed by a keyword and optionally a sub-command.

    This allows all similar patterns to be handled by a single regex, which should aid in parsing
    speed as well as reduce the burden of adding new commands.

    New commands are added by creating a CommandComponent object and adding this component to the
    MarkdownExtension via the addCommand method (see extensions/devel.py for an example).
    """
    PARSE_SETTINGS = False
    COMMANDS = base.MarkdownExtension.__COMMANDS__

    def createToken(self, match, parent):

        cmd = (match.group('command'), match.group('subcommand'))

        #TODO: Error check
        if cmd not in self.COMMANDS:
            msg = "The following command combination is unknown: '{} {}'."
            raise common.exceptions.TokenizeException(msg.format(*cmd))

        obj = self.COMMANDS[cmd]
        obj.settings, _ = common.parse_settings(obj.defaultSettings(), match.group('settings'))
        token = obj.createToken(match, parent)
        return token

    """
    def setup(self, value):
        MarkdownComponent.setup(self, value)
        for obj in self.COMMANDS.itervalues():
            obj.setup(value)
    """

class InlineCommand(CommandBase):
    RE = re.compile('\s*!(?P<command>\w+) (?P<subcommand>\w+) *(?P<settings>.*?)$',
                    flags=re.UNICODE|re.MULTILINE)

class BlockCommand(CommandBase):
    RE = re.compile(r'\s*^!(?P<command>\w+)!\s(?P<subcommand>\w+) *(?P<settings>.*?)?\n(?P<content>.*?)(^!\1-end!)',
                    flags=re.MULTILINE|re.DOTALL|re.UNICODE)

class FileCommand(CommandBase):
    RE = re.compile(r'\s*!(?P<command>\w+) (?P<filename>\S*?\.(?P<subcommand>\w+)) *(?P<settings>.*?)$', flags=re.UNICODE|re.MULTILINE)

class CommandRenderExtension(base.RenderExtension):
    def extend(self):
        pass
