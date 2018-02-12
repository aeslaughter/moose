"""
Extension for changing configure options within the page.
"""
import re
import collections
from moosedown.common import exceptions
from moosedown.tree import app_syntax
from moosedown import base
from moosedown.extensions import command

def make_extension(**kwargs):
    return AppSyntaxExtension(**kwargs)

class AppSyntaxExtension(command.CommandExtension):

    @staticmethod
    def defaultSettings():
        config = command.CommandExtension.defaultSettings()
        config['executable'] = (None, "The MOOSE executable to use for generating syntax.")
        return config

    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)

        exe = common.eval_path(self['executable'])
        self._app_syntax = app_syntax(exe)

    @property
    def syntax(self):
        return self._app_syntax

    def extend(self, reader, renderer):
        self.addCommand(SyntaxParametersCommand())

class SyntaxCommandBase(command.CommandComponent):
    COMMAND = 'syntax'

    def find(self, *args, **kwargs):
        return self.extension.syntax.find(*args, **kwargs)


class SyntaxParametersCommand(command.CommandComponent):
    SUBCOMMAND = 'parameters'



    def createToken(self, match, parent):

        print 'MATCH==================================='

        return parent
