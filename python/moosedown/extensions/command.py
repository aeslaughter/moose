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

    def extend(self, reader, renderer):
        #TODO: require core to be loaded


        reader.addBlock(FileCommand(), location='<moosedown.extensions.core.Code')
        reader.addBlock(InlineCommand(), location='>moosedown.extensions.command.FileCommand')
        reader.addBlock(BlockCommand(), location='>moosedown.extensions.command.InlineCommand')


#        self.addCommand(Include())

class MarkdownCommandComponent(base.TokenComponent):
    """
    Base Markdown component for creating commands.
    """
    COMMAND = None
    SUBCOMMAND = None


    @staticmethod
    def defaultSettings():
        #TODO: this is duplicate with core.MarkdownComponent
        settings = base.TokenComponent.defaultSettings()
        settings['style'] = (u'', "The style settings that are passed to the HTML flags.")
        settings['class'] = (u'', "The class settings to be passed to the HTML flags.")
        settings['id'] = (u'', "The class settings to be passed to the HTML flags.")
        return settings

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
    def __init__(self, *args, **kwargs):
        core.MarkdownComponent.__init__(self, *args, **kwargs)
        #self.__commands = dict()#base.MarkdownReader.__COMMANDS__ #TODO: this should be the storage, CommandExtension should add the addCommand method

    def createToken(self, match, parent):
        #print 'CommandBase:', match.groups()
        cmd = (match['command'], match['subcommand'])

        #TODO: Error check
        if cmd not in self.translator.reader._commands:
            msg = "The following command combination is unknown: '{} {}'."
            raise common.exceptions.TokenizeException(msg.format(*cmd))

        obj = self.translator.reader._commands[cmd]
        obj.settings, _ = common.parse_settings(obj.defaultSettings(), match['settings'])
        token = obj.createToken(match, parent)
        return token

    """
    def setup(self, value):
        MarkdownComponent.setup(self, value)
        for obj in self.COMMANDS.itervalues():
            obj.setup(value)
    """

class InlineCommand(CommandBase):
    RE = re.compile(r'\s*!(?P<command>\w+) (?P<subcommand>\w+)? *(?P<settings>.*?)$',
                    flags=re.UNICODE|re.MULTILINE)

class BlockCommand(CommandBase):
    RE = re.compile(r'\s*^!(?P<command>\w+)! *(?P<subcommand>\w+)? *(?P<settings>.*?)?\n(?P<content>.*?)(^!\1-end!)',
                    flags=re.MULTILINE|re.DOTALL|re.UNICODE)

class FileCommand(CommandBase):
    RE = re.compile(r'\s*!(?P<command>\w+) (?P<filename>\S*?\.(?P<subcommand>\w+)) *(?P<settings>.*?)$', flags=re.UNICODE|re.MULTILINE)
