"""
Extension for changing configure options within the page.
"""
import os
import re
import collections
import logging

import anytree

import mooseutils

import MooseDocs
from MooseDocs import common
from MooseDocs.base import components
from MooseDocs.common import exceptions
from MooseDocs.tree import html, tokens, syntax, app_syntax
from MooseDocs.extensions import floats

from MooseDocs.extensions import command

LOG = logging.getLogger(__name__)

def make_extension(**kwargs):
    return AppSyntaxExtension(**kwargs)

class InputParametersToken(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + \
                 [tokens.Property('syntax', ptype=syntax.SyntaxNodeBase, required=True)]

class AppSyntaxDisabledToken(tokens.Token):
    pass


class SyntaxToken(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + \
                 [tokens.Property('syntax', ptype=syntax.SyntaxNodeBase, required=True),
                  tokens.Property('actions', default=True, ptype=bool),
                  tokens.Property('objects', default=True, ptype=bool),
                  tokens.Property('subsystems', default=True, ptype=bool),
                  tokens.Property('groups', default=[], ptype=list)]

class AppSyntaxExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['executable'] = (None, "The MOOSE application executable to use for generating syntax.")
        config['includes'] = ([], "List of include directories to investigate for class information.")
        config['inputs'] = ([], "List of directories to interrogate for input files using an object.")
        config['disable'] = (False, "Disable running the MOOSE application executable and simply use place holder text.")
        return config

    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)

        self._app_syntax = None
        if not self['disable']:
            LOG.info("Reading MOOSE application syntax.")
            try:
                exe = common.eval_path(self['executable'])
                self._app_syntax = app_syntax(exe)
            except:
                msg = "Failed to load application executable from '%s', " \
                      "application syntax is being disabled."
                LOG.error(msg, self['executable'])

        LOG.info("Building MOOSE class database.")
        self._database = common.build_class_database(self['includes'], self['inputs'])

        self._cache = dict()

    @property
    def syntax(self):
        return self._app_syntax

    @property
    def database(self):
        return self._database


    def find(self, name, exc=exceptions.TokenizeException):

        try:
            return self._cache[name]
        except KeyError:
            pass

        node = anytree.search.find(self.syntax, filter_=lambda n: n.fullpath == name)

        if node is None:
            msg = "'{}' syntax was not recognized."
            raise exc(msg, name)

        return node

    def extend(self, reader, renderer):

        self.requires(floats)

        self.addCommand(SyntaxDescriptionCommand())
        self.addCommand(SyntaxParametersCommand())
        self.addCommand(SyntaxListCommand())
        self.addCommand(SyntaxInputsCommand())
        self.addCommand(SyntaxChildrenCommand())

        renderer.add(InputParametersToken, RenderInputParametersToken())
        renderer.add(SyntaxToken, RenderSyntaxToken())
        renderer.add(AppSyntaxDisabledToken, RenderAppSyntaxDisabledToken())

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
        if self.extension.syntax is None:
            AppSyntaxDisabledToken(parent, string=info[0])
            return parent

        if self.settings['syntax'] is None:
            args = info['settings'].split()
            if args and ('=' not in args[0]):
                self.settings['syntax'] = args[0]
        if self.settings['syntax']:
            obj = self.extension.find(self.settings['syntax'])
        else:
            obj = self.extension.syntax
        return self.createTokenFromSyntax(info, parent, obj)

    def createTokenFromSyntax(self, info, parent, obj):
        pass


class SyntaxParametersCommand(SyntaxCommandBase):
    SUBCOMMAND = 'parameters'

    def createTokenFromSyntax(self, info, parent, obj):
        return InputParametersToken(parent, syntax=obj, **self.attributes)

class SyntaxDescriptionCommand(SyntaxCommandBase):
    SUBCOMMAND = 'description'
    def createTokenFromSyntax(self, info, parent, obj):
        self.translator.reader.parse(parent, obj.description, group=MooseDocs.INLINE)
        return parent


class SyntaxChildrenCommand(SyntaxCommandBase):
    SUBCOMMAND = 'children'

    @staticmethod
    def defaultSettings():
        settings = SyntaxCommandBase.defaultSettings()
        settings['title'] = (u"Child Objects", "The heading to include for the file sections, use 'None' to remove the title.")
        settings['level'] = (2, "Heading level for section title.")
        return settings

    def createTokenFromSyntax(self, info, parent, obj):

        item = self.extension.database.get(obj.name, None)
        attr = getattr(item, self.SUBCOMMAND)
        if item and attr:

            if self.settings['title'].lower() != 'none':
                h = tokens.Heading(parent, level=self.settings['level'])
                self.translator.reader.parse(h, self.settings['title'], group=MooseDocs.INLINE)

            ul = tokens.UnorderedList(parent)
            for filename in attr:
                filename = unicode(filename)
                _, ext = os.path.splitext(filename)
                li = tokens.ListItem(ul)
                a = tokens.Link(li, url=filename, string=filename)
                modal = floats.Modal(a, bottom=True, title=filename)

                language = u'text' if ext == '.i' else u'cpp'
                tokens.Code(modal, language=language, code=common.read(os.path.join(MooseDocs.ROOT_DIR, filename)))

        return parent

class SyntaxInputsCommand(SyntaxChildrenCommand):
    SUBCOMMAND = 'inputs'
    @staticmethod
    def defaultSettings():
        settings = SyntaxChildrenCommand.defaultSettings()
        settings['title'] = (u"Input Files", settings['title'][1])
        return settings


class SyntaxListCommand(SyntaxCommandBase):
    SUBCOMMAND = 'list'

    @staticmethod
    def defaultSettings():
        settings = SyntaxCommandBase.defaultSettings()
        settings['groups'] = (None, "List of groups (apps) to include in the complete syntax list.")
        settings['actions'] = (True, "Include a list of Action objects in syntax.")
        settings['objects'] = (True, "Include a list of MooseObject objects in syntax.")
        settings['subsystems'] = (True, "Include a list of sub system syntax in the output.")
        return settings

    def createTokenFromSyntax(self, info, parent, obj):
        return SyntaxToken(parent,
                           syntax=obj,
                           actions=self.settings['actions'],
                           objects=self.settings['objects'],
                           subsystems=self.settings['subsystems'],
                           groups=self.settings['groups'].split() if self.settings['groups'] else [],
                           **self.attributes)


class RenderSyntaxToken(components.RenderComponent):
    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):

        active_groups = [group.lower() for group in token.groups]
        self._addSyntax(parent, token.syntax, active_groups, token.actions, token.objects, token.subsystems, 2)

    def _addSyntax(self, parent, syntax, active_groups, actions, objects, subsystems, level):

        groups = list(syntax.groups)
        if 'Framework' in groups:
            groups.remove('Framework')
            groups.insert(0, 'Framework')

        h = html.Tag(parent, 'h{}'.format(level), string=unicode(syntax.fullpath))

        collection = html.Tag(None, 'ul', class_='collection with-header')
        for group in groups:

            if active_groups and group.lower() not in active_groups:
                continue

            li = html.Tag(collection, 'li',
                          class_='moose-syntax-header collection-header',
                          string=unicode(mooseutils.camel_to_space(group)))

            count = len(collection.children)
            if actions:
                self._addItems(collection, syntax.actions(group=group), 'moose-syntax-actions')
            if objects:
                self._addItems(collection, syntax.objects(group=group), 'moose-syntax-objects')
            if subsystems:
                self._addItems(collection, syntax.syntax(group=group), 'moose-syntax-subsystems')

            if len(collection.children) == count:
                li.parent = None

            if collection.children:
                collection.parent=parent

    def _addItems(self, parent, items, cls):

        for obj in items:
            li = html.Tag(parent, 'li', class_='{} collection-item'.format(cls))
            html.Tag(li, 'a', class_='{}-name'.format(cls), string=unicode(obj.name)) #TODO: add href to html page

            if isinstance(obj, syntax.ObjectNode):
                desc = html.Tag(li, 'span', class_='{}-description'.format(cls))#, string=unicode(obj.description))

                ast = tokens.Token(None)
                self.translator.reader.parse(ast, unicode(obj.description), group=MooseDocs.INLINE)
                self.translator.renderer.process(desc, ast)


class RenderAppSyntaxDisabledToken(components.RenderComponent):
    def createHTML(self, token, parent):
        return html.Tag(parent, 'span', class_='moose-disabled')

    def createLatex(self, token, parent):
        pass

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
