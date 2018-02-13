"""
Extension for changing configure options within the page.
"""
import re
import collections

import anytree

from moosedown import common
from moosedown.base import components
from moosedown.common import exceptions
from moosedown.tree import html, tokens, syntax, app_syntax


from moosedown.extensions import command

def make_extension(**kwargs):
    return AppSyntaxExtension(**kwargs)

class InputParametersToken(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + \
                 [tokens.Property('syntax', ptype=syntax.SyntaxNodeBase, required=True)]

class AppSyntaxExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['executable'] = (None, "The MOOSE executable to use for generating syntax.")
        return config

    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)

        exe = common.eval_path(self['executable'])
        self._app_syntax = app_syntax(exe)

        self._cache = dict()

    @property
    def syntax(self):
        return self._app_syntax

    def find(self, name, exc=exceptions.TokenizeException):

        try:
            return self._cache[name]
        except KeyError:
            pass

        node = anytree.search.find(self.syntax, filter_=lambda n: n.fullpath == name)

        if node is None:
            msg = "'{}' syntax was not recongnized."
            raise exc(msg, name)

        return node

    def extend(self, reader, renderer):
        self.addCommand(SyntaxParametersCommand())

        renderer.add(InputParametersToken, RenderInputParametersToken())

class SyntaxCommandBase(command.CommandComponent):
    COMMAND = 'syntax'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['syntax'] = (None, "The name of the syntax to extract. If the name of the syntax " \
                                    "is the first item in the settings the 'syntax=' may be " \
                                    "omitted, e.g., `!syntax parameters /Kernels/Diffusion`.")
        return settings

    def createToken(self, info, parent):
        if self.settings['syntax'] is None:
            args = info['settings'].split()
            self.settings['syntax'] = args[0]


class SyntaxParametersCommand(SyntaxCommandBase):
    SUBCOMMAND = 'parameters'

    def createToken(self, info, parent):
        SyntaxCommandBase.createToken(self, info, parent)
        obj = self.extension.find(self.settings['syntax'])
        return InputParametersToken(parent, syntax=obj, **self.attributes)

class RenderInputParametersToken(components.RenderComponent):

    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):

        # Parameters dict()
        groups = collections.OrderedDict()
        groups['Required'] = dict()
        groups['Optional'] = dict()


        for param in token.syntax.parameters.itervalues() or []:

            group = param['group_name']
            name = param['name']

            if name == 'type':
                continue

            if not group and param['required']:
                group = 'Required'
            elif not group and not param['required']:
                group = 'Optional'

            if group not in groups:
                groups[group] = dict()
            groups[group][name] = param


        html.Tag(parent, 'h2', string=unicode('Input Parameters'))

        for group, params in groups.iteritems():

            if not params:
                continue

            h = html.Tag(parent, 'h3', string=unicode('{} Parameters'.format(group.title())))
            if group == 'Required':
                h['data-details-open'] = 'open'
            else:
                h['data-details-open'] = 'close'

            ul = html.Tag(parent, 'ul', class_='collapsible')
            ul['data-collapsible'] = "expandable"

            for name, param in params.iteritems():
                _insert_parameter(ul, name, param)

        return parent

def _insert_parameter(parent, name, param):

    if param['deprecated']:
        return

    li = html.Tag(parent, 'li')
    header = html.Tag(li, 'div', class_='collapsible-header')
    body = html.Tag(li, 'div', class_='collapsible-body')



    html.Tag(header, 'span', class_='moose-parameter-name', string=name)
    default = _format_default(param)
    if default:
        html.Tag(header, 'span', class_='moose-parameter-header-default', string=default)

        p = html.Tag(body, 'p', class_='moose-parameter-description-default')
        html.Tag(p, 'span', string=u'Default:')
        html.String(p, content=default)

    cpp_type = param['cpp_type']
    p = html.Tag(body, 'p', class_='moose-parameter-description-cpptype')
    html.Tag(p, 'span', string=u'C++ Type:')
    html.String(p, content=cpp_type)


    p = html.Tag(body, 'p', class_='moose-parameter-description')

    desc = param['description']
    if desc:
        html.Tag(header, 'span', class_='moose-parameter-header-description', string=unicode(desc))
        html.Tag(p, 'span', string=u'Description:')
        html.String(p, content=unicode(desc))



def _format_default(parameter):
    """
    Convert the supplied parameter into a format suitable for output.

    Args:
        parameter[str]: The parameter dict() item.
        key[str]: The current key.
    """

    ptype = parameter['cpp_type']
    param = parameter.get('default', '')

    if ptype == 'bool':
        param = repr(param in ['True', '1'])

    return unicode(param) if param else None
