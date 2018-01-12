import re
from moosedown import base
from moosedown.extensions import command

def make_extension(**kwargs):
    return MetaExtension(**kwargs)

class MetaExtension(base.Extension):

    def extend(self, reader, renderer):
        reader.addCommand(MetaCommand())

class MetaCommand(command.BlockCommand):
    COMMAND = 'meta'
    SUBCOMMAND = None

    def createToken(self, match, parent):

        for data in match.group('content').strip(' \n').split('\n'):
            key, value = data.split('=')
            self.translator.node[key] = eval(value)

        return parent
