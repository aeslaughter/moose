"""
Extension for changing configure options within the page.
"""
import re
import collections
from moosedown.common import exceptions
from moosedown import base
from moosedown.extensions import command

def make_extension(**kwargs):
    return ConfigExtension(**kwargs)

class ConfigExtension(command.CommandExtension):
    def extend(self, reader, renderer):
        self.addCommand(ConfigCommand())

class ConfigCommand(command.CommandComponent):
    COMMAND = 'config'
    SUBCOMMAND = None #TODO: make (Renderer, Extensions, Translator, etc... for available input blocks)
                      # TODO: Extensions should loop over all avaiable and apply if the parameter is the same...
    def createToken(self, match, parent):

        config = dict(Reader=dict(), Renderer=dict())

        content = match['inline'] if 'inline' in match else match['block']
        for data in content.strip(' \n').split('\n'):
            key, value = data.split('=')
            block, item = key.split('/', 1)

            if block not in config:
                msg = "The supplied block '{}' is unknown, only config options for the " \
                      "Extensions, Reader, and Render block are suppored."
                raise exceptions.TokenizeException(msg, block)

            config[block][item] = eval(value)

        #TODO: skip if not an option
        self.translator.reader.update(**config['Reader'])
        self.translator.renderer.update(**config['Renderer'])

        return parent
