import os
import MooseDocs
from MooseDocs.base import components
from MooseDocs.extensions import command
from MooseDocs.tree import tokens, html
from MooseDocs.tree.base import Property

#pylint: disable=doc-string

def make_extension(**kwargs):
    return GlobalExtension(**kwargs)

class GlobalExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['shortcuts'] = (dict(), "Key-value pairs to insert as shortcuts.")
        return config

    def extend(self, reader, renderer):
        pass

    def postTokenize(self, ast):
        for key, value in self['shortcuts'].iteritems():
            tokens.Shortcut(ast, key=unicode(key), link=unicode(key), content=unicode(value))
