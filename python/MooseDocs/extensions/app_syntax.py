#pylint: disable=missing-docstring
####################################################################################################
#                                    DO NOT MODIFY THIS HEADER                                     #
#                   MOOSE - Multiphysics Object Oriented Simulation Environment                    #
#                                                                                                  #
#                              (c) 2010 Battelle Energy Alliance, LLC                              #
#                                       ALL RIGHTS RESERVED                                        #
#                                                                                                  #
#                            Prepared by Battelle Energy Alliance, LLC                             #
#                               Under Contract No. DE-AC07-05ID14517                               #
#                               With the U. S. Department of Energy                                #
#                                                                                                  #
#                               See COPYRIGHT for full restrictions                                #
####################################################################################################
#pylint: enable=missing-docstring

import os
import logging
import collections

from markdown.util import etree
from markdown.inlinepatterns import Pattern
from MooseMarkdownExtension import MooseMarkdownExtension
from MooseMarkdownCommon import MooseMarkdownCommon
from MooseObjectParameterTable import MooseObjectParameterTable
import MooseDocs
from MooseDocs.common.MooseAppSyntax import SyntaxNode, MooseObjectNode
from . import misc   # used for addScrollSpy function
from .. import common

LOG = logging.getLogger(__name__)

class AppSyntaxExtension(MooseMarkdownExtension):
    """
    Extensions that comprise the MOOSE flavored markdown.
    """
    @staticmethod
    def defaultConfig():
        """Default settings for MooseMarkdownCommon."""

        config = MooseMarkdownExtension.defaultConfig()
        config['executable'] = ['', "The executable to utilize for generating application syntax."]
        config['repo'] = ['', "The remote repository to create hyperlinks."]
        config['links'] = [dict(), "The set of paths for generating input file and source code "
                                   "links to objects."]
        config['install'] = ['', "The location to install system and object documentation."]
        config['hide'] = [dict(), "Suppress warnings for syntax listed in this dictionary."]
        return config

    def __init__(self, **kwargs):
        super(AppSyntaxExtension, self).__init__(**kwargs)

        # Storage for the MooseAppSyntax and MooseLinkDatabase object
        self.__app_syntax = None

    def getMooseAppSyntax(self):
        """
        Return the MooseAppSyntax object.
        """
        return self.__app_syntax

    def extendMarkdown(self, md, md_globals):
        """
        Builds the extensions for MOOSE flavored markdown.
        """
        md.registerExtension(self)

        # Create a config object
        config = self.getConfigs()

        # Build syntax from JSON
        exe = MooseDocs.abspath(self.getConfig('executable'))
        self.__app_syntax = common.MooseAppSyntax(exe, hide=config['hide'])

        # Populate the database for input file and children objects
        LOG.debug('Creating input file and source code use database.')
        database = common.MooseLinkDatabase(repo=config['repo'], links=config['links'])

        # Inline Patterns
        system = MooseCompleteSyntax(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_complete_syntax', system, '_begin')

        params = MooseParameters(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_syntax_parameters', params, '_begin')

        desc = MooseDescription(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_syntax_description', desc, '_begin')

        child_list = MooseFileList(markdown_instance=md,
                                   database=database.children,
                                   title='Child Objects',
                                   command='children',
                                   **config)
        md.inlinePatterns.add('moose_child_list', child_list, '_begin')

        input_list = MooseFileList(markdown_instance=md,
                                   database=database.inputs,
                                   title='Input Files',
                                   command='inputs',
                                   **config)
        md.inlinePatterns.add('moose_input_list', input_list, '_begin')

        object_list = MooseObjectList(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_object_list', object_list, '_begin')

        action_list = MooseActionList(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_action_list', action_list, '_begin')

        subsystem_list = MooseSubSystemList(markdown_instance=md, **config)
        md.inlinePatterns.add('moose_subsystem_list', subsystem_list, '_begin')

def makeExtension(*args, **kwargs): #pylint: disable=invalid-name
    """
    Create the AppSyntaxExtension.
    """
    return AppSyntaxExtension(*args, **kwargs)

class MooseSyntaxBase(MooseMarkdownCommon, Pattern):
    """
    Base for MOOSE system/object pattern matching.

    Args:
      regex[str]: The regular expression to match.
      yaml[MooseYaml]: The MooseYaml object for the application.
      syntax[dict]: A dictionary of MooseApplicatinSyntax objects.
    """
    @staticmethod
    def defaultSettings():
        """Default settings for MooseSyntaxBase."""
        settings = MooseMarkdownCommon.defaultSettings()
        settings['actions'] = (True, "Enable/disable action syntax lookup (this is used for "
                                     "shared syntax such as BCs/Pressue).")
        settings['objects'] = (True, "Enable/disable MooseObject syntax lookup (this is used for "
                                     "shared syntax such as BCs/Pressue).")
        return settings

    def __init__(self, regex, markdown_instance=None, syntax=None, **kwargs):
        MooseMarkdownCommon.__init__(self, **kwargs)
        Pattern.__init__(self, regex, markdown_instance)
        self._syntax = syntax

    def initMatch(self, match):
        """
        Initialize method for return the nodes and settings.
        """

        # Extract Syntax and Settings
        syntax = match.group('syntax')
        settings = self.getSettings(match.group('settings'))

        # Locate the node
        if settings['actions'] and settings['objects']:
            filter_ = lambda n: syntax == n.full_name
        elif settings['actions']:
            filter_ = lambda n: syntax == n.full_name and not isinstance(n, MooseObjectNode)
        elif settings['objects']:
            filter_ = lambda n: syntax == n.full_name and isinstance(n, MooseObjectNode)
        else:
            return self.createErrorElement("Both the 'action' and 'object' flags cannot be False.")

        nodes = self._syntax.findall(syntax=syntax, filter_=filter_)
        return nodes, settings

    def checkForErrors(self, nodes, match, unique=True):
        """
        Perform error checking on the nodes.
        """

        syntax = match.group('syntax')
        command = match.group('command')

        # Failed to locate syntax
        if not nodes:
            return 'Failed to locate MooseObject or Action for the command: `!syntax {} {}` ' \
                   'in the file {}'.format(str(command), str(syntax),
                                           self.markdown.current.source())

        # Non-unique
        if unique and len(nodes) > 1:
            msg = 'The syntax provided is not unique, the following objects were located for the ' \
                  'command `!syntax {} {}` in the file {}'.format(str(command), str(syntax),
                                                                  self.markdown.current.source())
            for node in nodes:
                msg += '\n    {}'.format(node.syntax)
            return msg

        return None

class MooseParameters(MooseSyntaxBase):
    """
    Creates parameter tables for Actions and MooseObjects.
    """

    RE = r'^!syntax\s+(?P<command>parameters)\s+(?P<syntax>.*?)(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        """Default settings for MooseParameters."""
        settings = MooseSyntaxBase.defaultSettings()
        settings['title'] = ('Input Parameters', "Title to include prior to the parameter table.")
        settings['title_level'] = (2, "The HTML heading level to apply to the title")
        return settings

    def __init__(self, **kwargs):
        super(MooseParameters, self).__init__(self.RE, **kwargs)

    def handleMatch(self, match):
        """
        Return table(s) of input parameters.
        """

        nodes, settings = self.initMatch(match)
        msg = self.checkForErrors(nodes, match)
        if msg:
            return self.createErrorElement(msg)
        info = nodes[0]

        # Parameters dict()
        parameters = dict()
        if isinstance(info, SyntaxNode):
            for action in info.actions():
                if action.parameters is not None:
                    parameters.update(action.parameters)
        else:
            parameters.update(info.parameters)

        # Create the tables (generate 'Required' and 'Optional' initially so that they come out in
        # the proper order)
        tables = collections.OrderedDict()
        tables['Required'] = MooseObjectParameterTable()
        tables['Optional'] = MooseObjectParameterTable()

        # Loop through the parameters in yaml object
        for param in parameters.itervalues() or []:
            name = param['group_name']
            if not name and param['required']:
                name = 'Required'
            elif not name and not param['required']:
                name = 'Optional'

            if name not in tables:
                tables[name] = MooseObjectParameterTable()
            tables[name].addParam(param)

        # Produces a debug message if parameters are empty, but generally we just want to include
        # the !parameters command, if parameters exist then a table is produce otherwise nothing
        # happens. This will allow for parameters to be added and the table appear if it was empty.
        if not any(tables.values()):
            LOG.debug('Unable to locate parameters for %s.', info.name)
        else:
            el = self.applyElementSettings(etree.Element('div'), settings)
            if settings['title']:
                title = etree.SubElement(el, 'h{}'.format(str(settings['title_level'])))
                title.text = settings['title']
            for key, table in tables.iteritems():
                if table:
                    subtitle = etree.SubElement(el, 'h{}'.format(str(settings['title_level'] + 1)))
                    subtitle.text = '{} {}'.format(key, 'Parameters')
                    el.append(table.html())
            return el

class MooseDescription(MooseSyntaxBase):
    """
    Creates parameter tables for Actions and MooseObjects.
    """
    RE = r'^!syntax\s+(?P<command>description)\s+(?P<syntax>.*?)(?:$|\s+)(?P<settings>.*)'

    def __init__(self, **kwargs):
        super(MooseDescription, self).__init__(self.RE, **kwargs)

    def handleMatch(self, match):
        """
        Return the class description html element.
        """
        # Extract Syntax and Settings
        nodes, settings = self.initMatch(match)
        msg = self.checkForErrors(nodes, match)
        if msg:
            return self.createErrorElement(msg)
        info = nodes[0]

        # Error if Syntax node (MooseObject or Action needs to be given in this case)
        if isinstance(info, SyntaxNode):
            msg = "The given syntax is not associated with a specific MooseObject or Action, " \
                  "include the Action or MooseObject class name:\n    {} in the file {}." \
                  .format(match.group(0), self.markdown.current.source())
            return self.createErrorElement(msg)

        # Create an Error element, but do not produce warning/error LOG because the
        # moosedocs check/generate commands produce errors.
        if info.description is None:
            msg = "Failed to locate class description for {} syntax in the file {}." \
                  .format(info.name, self.markdown.current.source())
            return self.createErrorElement(msg, error=False)

        # Create the html element with supplied styles
        el = self.applyElementSettings(etree.Element('p'), settings)
        el.text = info.description
        return el

class MooseFileList(MooseSyntaxBase):
    """
    A file list creation object designed to work with MooseLinkDatabase information.

    Args:
        database[dict]: The MooseLinkDatabase dictionary to consider.
        repo[str]: The repository for creating links to GitHub/GitLab.
        title[str]: The default title.
        command[str]: The command to associate with the "!syntax" keyword.
    """
    RE = r'^!syntax\s+(?P<command>{})\s+(?P<syntax>.*?)(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseSyntaxBase.defaultSettings()
        settings['title'] = ('default', "The title display prior to tables ('default' will apply "
                                        "a generic title.).")
        settings['title_level'] = (2, "The HTML heading level to apply to the title.")
        return settings

    def __init__(self, database=None, repo=None, title=None, command=None, **kwargs):
        super(MooseFileList, self).__init__(self.RE.format(command), **kwargs)
        self._database = database
        self._repo = repo
        self._title = title

    def handleMatch(self, match):
        """
        Create the list element.
        """

        # Extract the desired node.
        nodes, settings = self.initMatch(match)
        msg = self.checkForErrors(nodes, match)
        if msg:
            return self.createErrorElement(msg)
        info = nodes[0]

        # Update title
        if (settings['title'] is not None) and (settings['title'].lower() == 'default'):
            settings['title'] = self._title

        # Print the item information
        el = self.applyElementSettings(etree.Element('div'), settings)
        if settings['title'] is not None:
            el.set('id', '#{}'.format(settings['title'].lower().replace(' ', '-')))
        if settings['title_level'] == 2:
            el.set('class', 'section scrollspy')
        self._listhelper(el, info, settings)
        return el


    def _listhelper(self, parent, info, settings):
        """
        Helper method for dumping link lists.

        Args:
          parent[etree.Element]: The parent element the headers and lists are to be applied
          info[SyntaxNode]: The desired object from which the list will be created.
          settings[dict]: The current settings.
        """
        level = int(settings['title_level'])

        has_items = False
        for k, db in self._database.iteritems():
            if info.name in db:
                has_items = True
                h3 = etree.SubElement(parent, 'h{}'.format(level + 1))
                h3.text = k
                ul = etree.SubElement(parent, 'ul')
                ul.set('style', "max-height:350px;overflow-y:Scroll")
                for j in db[info.name]:
                    ul.append(j.html())

        if has_items and settings['title'] is not None:
            h2 = etree.Element('h{}'.format(level))
            h2.text = settings['title']
            parent.insert(0, h2)


class MooseCompleteSyntax(MooseMarkdownCommon, Pattern):
    """
    Display the complete system syntax for the compiled application.

    The static methods of this class are used by the 'objects' and 'actions' command as well.
    """
    RE = r'^!syntax\s+complete(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseMarkdownCommon.defaultSettings()
        settings['groups'] = (None, "The configured 'groups' to include.")
        return settings

    def __init__(self, markdown_instance=None, syntax=None, **kwargs):
        MooseMarkdownCommon.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)
        self._syntax = syntax
        self._install = kwargs.get('install')

    def handleMatch(self, match):
        """
        Creates complete list of objects.
        """
        settings = self.getSettings(match.group('settings'))
        groups = self.sortGroups(self._syntax, settings)

        div = etree.Element('div')
        div.set('class', 'moose-system-list')

        for obj in self._syntax.syntax():
            self.addHeader(div, obj, self._install)
            self.addObjects(div, obj, groups, self._install)

        misc.ScrollContents.addScrollSpy(div)
        return div

    @staticmethod
    def sortGroups(syntax, settings):
        """
        Re-order groups to begin with 'framework' and limit groups based on settings.
        """

        # Get the dict() of groups to include
        groups = syntax.groups()
        if settings['groups'] is not None:
            for key in groups.keys():
                if key not in settings['groups']:
                    groups.pop(key)

        # Re-order
        framework = groups.pop('framework', None)
        groups = sorted(groups.items())
        if framework is not None:
            groups.insert(0, ('framework', framework))

        return groups

    @staticmethod
    def addHeader(div, obj, install):
        """
        Adds syntax header.
        """
        level = obj.full_name.count('/') + 1
        hid = obj.full_name.strip('/').replace('/', '-').lower()

        h = etree.SubElement(div, 'h{}'.format(level))
        h.text = obj.full_name.strip('/')
        h.set('id', hid)

        a = etree.SubElement(h, 'a')
        a.set('href', os.path.join(install, obj.full_name.strip('/'), 'index.md'))
        if obj.hidden:
            a.set('data-moose-disable-link-error', '1')

        i = etree.SubElement(a, 'i')
        i.set('class', 'material-icons')
        i.text = 'input'

        for group in obj.groups.itervalues():
            chip = etree.SubElement(h, 'div')
            chip.set('class', 'chip moose-chip')
            chip.text = group

    @staticmethod
    def addObjects(div, node, groups, install):
        """
        Add all MooseObject to the <div> container.
        """
        MooseCompleteSyntax._addItemsHelper(div, groups, install, node.objects, 'Objects')

    @staticmethod
    def addActions(div, node, groups, install):
        """
        Add all Actions to the <div> container.
        """
        MooseCompleteSyntax._addItemsHelper(div, groups, install, node.actions, 'Actions')

    @staticmethod
    def addSyntax(div, node, groups, install):
        """
        Add all SyntaxNode (i.e., subsystems) to the <div> container.
        """
        MooseCompleteSyntax._addItemsHelper(div, groups, install, node.syntax, 'Systems')

    @staticmethod
    def _addItemsHelper(div, groups, install, func, title,):
        """
        Helper for adding objects/actions to the supplied div object.
        """
        el = MooseDocs.common.MooseCollapsible()
        for folder, group in groups:
            objects = func(group=folder)
            if objects:
                el.addHeader('{} {}'.format(group, title))
                for obj in objects:
                    a = etree.Element('a')
                    a.text = obj.name
                    a.set('href', obj.markdown(install))
                    if obj.hidden:
                        a.set('data-moose-disable-link-error', '1')

                    if hasattr(obj, 'description'):
                        el.addItem(a, obj.description)
                    else:
                        el.addItem(a)

        if el:
            div.append(el.element())

class MoosePartialSyntax(MooseSyntaxBase):
    """
    Creates dynamic lists for MooseObjects or Actions.
    """
    RE = r'^!syntax\s+(?P<command>{})\s+(?P<syntax>.*?)(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseSyntaxBase.defaultSettings()
        settings['title'] = (None, "Title to include prior to the syntax list.")
        settings['title_level'] = (2, "The HTML heading level to apply to the title")
        settings['groups'] = (None, "The configured 'groups' to include.")
        return settings

    def __init__(self, syntax=None, command=None, **kwargs):
        MooseSyntaxBase.__init__(self, self.RE.format(command), syntax=syntax, **kwargs)
        self._install = kwargs.get('install')

    def addSyntax(self, div, info, groups):
        """
        Abstract method for the adding either the action of object list.
        """
        pass

    def handleMatch(self, match):
        """
        Handle the regex match for this extension.
        """

        # Extract the desired nodes
        syntax = match.group('syntax')
        nodes, settings = self.initMatch(match)
        msg = self.checkForErrors(nodes, match)
        if msg:
            return self.createErrorElement(msg)
        info = nodes[0]

        # Error if not a SyntaxNode
        if not isinstance(info, SyntaxNode):
            msg = "The given syntax '{}' returned a MooseObject of Action node in file {}." \
                  .format(syntax, self.markdown.current.source())
            return self.createErrorElement(msg)

        # Create and return the element
        div = etree.Element('div')
        div.set('class', 'moose-system-list')
        if settings['title'] is not None:
            h = etree.SubElement(div, 'h{}'.format(int(settings['title_level'])))
            h.text = settings['title']
        groups = MooseCompleteSyntax.sortGroups(self._syntax, settings)
        self.addSyntax(div, info, groups)
        return div

class MooseObjectList(MoosePartialSyntax):
    """
    Create the "!syntax objects" command.
    """
    @staticmethod
    def defaultSettings():
        """Add default settings for object lists."""
        settings = MoosePartialSyntax.defaultSettings()
        settings['title'] = ("Available Sub-Objects", settings['title'][1])
        return settings

    def __init__(self, **kwargs):
        super(MooseObjectList, self).__init__(command='objects', **kwargs)

    def addSyntax(self, div, info, groups):
        """
        Adds objects.
        """
        MooseCompleteSyntax.addObjects(div, info, groups, self._install)

class MooseActionList(MoosePartialSyntax):
    """
    Create the "!syntax actions" command.
    """
    @staticmethod
    def defaultSettings():
        """Add default settings for action lists."""
        settings = MoosePartialSyntax.defaultSettings()
        settings['title'] = ("Available Actions", settings['title'][1])
        return settings

    def __init__(self, **kwargs):
        super(MooseActionList, self).__init__(command='actions', **kwargs)

    def addSyntax(self, div, info, groups):
        """
        Adds actions.
        """
        MooseCompleteSyntax.addActions(div, info, groups, self._install)


class MooseSubSystemList(MoosePartialSyntax):
    """
    Create the "!syntax subsystems" command.
    """
    @staticmethod
    def defaultSettings():
        """Add default settings for subsystem lists."""
        settings = MoosePartialSyntax.defaultSettings()
        settings['title'] = ("Available Sub-Systems", settings['title'][1])
        return settings

    def __init__(self, **kwargs):
        super(MooseSubSystemList, self).__init__(command='subsystems', **kwargs)

    def addSyntax(self, div, info, groups):
        """
        Adds Sub-Systems.
        """
        MooseCompleteSyntax.addSyntax(div, info, groups, self._install)
