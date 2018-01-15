import re
import collections
from moosedown import base
from moosedown.extensions import command

def make_extension(**kwargs):
    return ConfigExtension(**kwargs)

class ConfigExtension(base.Extension):

    def extend(self, reader, renderer):
        reader.addCommand(ConfigCommand())

class ConfigCommand(command.BlockCommand):
    COMMAND = 'config'
    SUBCOMMAND = None

    def createToken(self, match, parent):

        config = dict(Reader=dict(), Renderer=dict())
        for data in match.group('content').strip(' \n').split('\n'):
            key, value = data.split('=')
            block, item = key.split('/', 1)

            if block not in config:
                msg = "The supplied block '{}' is unknown, only config options for the " \
                      "Extensions, Reader, and Render block are suppored."
                raise KeyError(msg.format(block))

            config[block][item] = eval(value)

        #TODO: skip if not an option
        self.translator.reader.update(**config['Reader'])
        self.translator.renderer.update(**config['Renderer'])

        return parent
