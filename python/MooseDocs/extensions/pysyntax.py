#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import importlib
from ..common import exceptions
from ..base import components
from ..tree import tokens, html
from . import command, core

def make_extension(**kwargs):
    return PyAppSyntaxExtension(**kwargs)

PyParameterToken = tokens.newToken('PyParameterToken', parameter=None)
PyInputParametersToken = tokens.newToken('PyInputParametersToken', pyobject=None, level=2)

class PyAppSyntaxExtension(command.CommandExtension):
    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        return config

    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)

    def extend(self, reader, renderer):
        self.requires(core, command)#, floats, table, autolink, materialicon)
        self.addCommand(reader, PySyntaxParameters())

        renderer.add('PyInputParametersToken', RenderPyInputParametersToken())
        renderer.add('PyParameterToken', RenderPyParameterToken())


class PySyntaxParameters(command.CommandComponent):
    COMMAND = 'pysyntax'
    SUBCOMMAND = 'parameters'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['module'] = (None, "The name of the module containing the object.")
        settings['object'] = (None, "The name of the object to import from the 'module'.")
        return settings

    def createToken(self, parent, info, page):
        # TODO: Merge with devel.py extension
        try:
            mod = importlib.import_module(self.settings['module'])
        except ImportError:
            msg = "Unable to load the '{}' module."
            raise exceptions.MooseDocsException(msg, self.settings['module'])

        try:
            obj = getattr(mod, self.settings['object'])
        except AttributeError:
            msg = "Unable to load the '{}' attribute from the '{}' module."
            raise exceptions.MooseDocsException(msg, self.settings['object'],
                                                self.settings['module'])


        token = PyInputParametersToken(parent, pyobject=self.settings['object'])
        for param in obj.validParams()._InputParameters__parameters.values():
            PyParameterToken(token, parameter=param)
        return parent


class RenderPyInputParametersToken(components.RenderComponent):
    def createMaterialize(self, parent, token, page):
        html.Tag(parent, 'h{}'.format(token['level'], string='{} Parameters'.format(token['pyobject'])))
        ul = html.Tag(parent, 'ul', class_='collapsible')
        return ul

class RenderPyParameterToken(components.RenderComponent):
    def createMaterialize(self, parent, token, page):
        param = token['parameter']

        li = html.Tag(parent, 'li')

        header = html.Tag(li, 'div', class_='collapsible-header')
        html.String(header, content=param.name)

        body = html.Tag(li, 'div', class_='collapsible-body')
        html.String(body, content=param.doc)

        return parent
