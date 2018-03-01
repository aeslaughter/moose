#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
#pylint: enable=missing-docstring

import os
import re
import collections
import logging
import copy

import anytree

import mooseutils

import MooseDocs
from .base import NodeBase, Property

LOG = logging.getLogger(__name__)

class SyntaxNodeBase(NodeBase):
    """
    Node for MOOSE syntax that serves as the parent for actions/objects.
    """
    PROPERTIES = [Property('hidden', ptype=bool, default=False)]

    # Default documentation destinations for MOOSE and Modules
    DESTINATIONS = dict()
    DESTINATIONS['XFEM'] = 'modules/xfem/doc/content/documentation/systems'
    DESTINATIONS['NavierStokes'] = 'modules/navier_stokes/doc/content/documentation/systems'
    DESTINATIONS['TensorMechanics'] = 'modules/tensor_mechanics/doc/content/documentation/systems'
    DESTINATIONS['PhaseField'] = 'modules/phase_field/doc/content/documentation/systems'
    DESTINATIONS['Rdg'] = 'rdg', 'modules/rdg/doc/content/documentation/systems'
    DESTINATIONS['Contact'] = 'modules/contact/doc/content/documentation/systems'
    DESTINATIONS['SolidMechanics'] = 'modules/solid_mechanics/doc/content/documentation/systems'
    DESTINATIONS['HeatConduction'] = 'modules/heat_conduction/doc/content/documentation/systems'
    DESTINATIONS['Framework'] = 'framework/doc/content/documentation/systems'
    DESTINATIONS['StochasticTools'] = 'modules/stochastic_tools/doc/content/documentation/systems'
    DESTINATIONS['Misc'] = 'modules/misc/doc/content/documentation/systems'
    DESTINATIONS['FluidProperties'] = 'modules/fluid_properties/doc/content/documentation/systems'
    DESTINATIONS['ChemicalReactions'] = 'modules/chemical_reactions/doc/content/documentation/systems'
    DESTINATIONS['LevelSet'] = 'modules/level_set/doc/content/documentation/systems'
    DESTINATIONS['PorousFlow'] = 'modules/porous_flow/doc/content/documentation/systems'
    DESTINATIONS['Richards'] = 'modules/richards/doc/content/documentation/systems'

    STUB_HEADER = '<!-- MOOSE Documentation Stub: Remove this when content is added. -->\n'

    def __init__(self, *args, **kwargs):
        NodeBase.__init__(self, *args, **kwargs)
        self.__hidden = False
        self.__check_status = None
        self._groups = set()

    @property
    def groups(self):
        """
        Return groups associated with this node or entire tree (i.e., where the syntax is defined).
        """
        out = copy.copy(self._groups)
        for node in self.descendants:
            out.update(node.groups)
        return out

    @property
    def fullpath(self):
        """
        Return the node full path.
        """
        out = []
        node = self
        while (node is not None):
            out.append(node.name)
            node = node.parent
        return '/'.join(reversed(out))

    def findfull(self, name, maxlevel=None):
        """
        Search for a node, by full name.
        """
        for node in anytree.PreOrderIter(self, maxlevel=maxlevel):
            if node.fullpath == name:
                return node

    def syntax(self, *args, **kwargs):
        """
        Return SyntaxNode nodes (see __nodeFinder).
        """
        return self.__nodeFinder(SyntaxNode, *args, **kwargs)

    def objects(self, *args, **kwargs):
        """
        Return MooseObjectNode nodes (see __nodeFinder).
        """
        return self.__nodeFinder(MooseObjectNode, *args, **kwargs)

    def actions(self, *args, **kwargs):
        """
        Return ActionNode nodes (see __nodeFinder).
        """
        return self.__nodeFinder(ActionNode, *args, **kwargs)

    def markdown(self, *args, **kwargs):
        """
        Return the expected markdown file name.
        """
        raise NotImplementedError("The 'markdown' method must return the expected markdown "
                                  "filename.")

    def check(self, generate=False, groups=None, update=None):
        """
        Check that the expected documentation exists.

        Return:
            True, False, or None, where True indicates that the page exists, False indicates the
            page does not exist or doesn't contain content, and None indicates that the page is
            hidden.
        """
        if groups is None:
            groups = self.groups

        if self.hidden:
            LOG.debug("Skipping documentation check for %s, it is hidden.", self.fullpath)

        else:
            # Locate all the possible locations for the markdown
            filenames = []
            for group in self.groups:
                install = SyntaxNodeBase.DESTINATIONS.get(group, 'doc/content/systems')
                filename = os.path.join(MooseDocs.ROOT_DIR, install, self.markdown())
                filenames.append((filename, os.path.isfile(filename)))

            # Determine the number of files that exist
            count = sum([x[1] for x in filenames])

            # Error if multiple files exist
            if count > 1:
                msg = "Multiple markdown files were located for the '%s' syntax:"
                for filename, exists in filenames:
                    if exists:
                        msg += '\n  {}'.format(filename)
                LOG.error(msg, self.fullpath)

            # Error if no files exist
            elif count == 0:
                msg = "No documentation for %s, documentation for this object should be created " \
                      "in one of the following locations:"
                for filename, _ in filenames:
                    msg += '\n  {}'.format(filename)
                LOG.error(msg, self.fullpath)

                if generate:
                    if not os.path.exists(os.path.dirname(filename)):
                        os.makedirs(os.path.dirname(filename))
                    LOG.info('Creating stub page for %s %s', self.fullpath, filename)
                    with open(filename, 'w') as fid:
                        content = self._defaultContent()
                        if not isinstance(content, str):
                            raise TypeError("The _defaultContent method must return a str.")
                        fid.write(content)
            else:
                for name, exists in filenames:
                    if exists:
                        filename = name

                with open(filename, 'r') as fid:
                    lines = fid.readlines()

                if lines and self.STUB_HEADER in lines[0]:
                    LOG.error("A MOOSE generated stub page for %s exists, but no content was "
                              "added. Add documentation content to %s.", self.name, filename)
                    if update:
                        LOG.info("Updating stub page for %s in file %s.", self.name, filename)
                        with open(filename, 'w') as fid:
                            content = self._defaultContent()
                            if not isinstance(content, str):
                                raise TypeError("The _defaultContent method must return a str.")
                            fid.write(content)

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        raise NotImplementedError("The _defaultContent method must be defined in child classes "
                                  "and return a string.")

    def __nodeFinder(self, node_type, syntax='', group=None, recursive=False):
        """
        A helper method for finding nodes of a given type, syntax, and group.

        Inputs:
            node_type[NodeCore]: The type of node to consider.
            syntax: (optional) The syntax that must be within the object 'fullpath' property.
            group: (optional) The group to limit the search.
            recursive: When True the search will look through all nodes in the entire tree, when
                       False only the children of the node are considered.
        """
        if recursive:
            filter_ = lambda node: (syntax in node.fullpath) and \
                                   isinstance(node, node_type) and \
                                   (group is None or group in node.groups)
            return self.findall(filter_=filter_)

        else:
            return [node for node in self.children if (syntax in node.fullpath) and \
                                                      isinstance(node, node_type) and \
                                                      (group is None or group in node.groups)]

    def __repr__(self):
        """
        Print the node name.
        """
        oname = self.__class__.__name__[:-4]
        msg = '{}: {} hidden={} groups={}'.format(oname,
                                                  str(self.fullpath),
                                                  self.hidden,
                                                  self.groups)
        return mooseutils.colorText(msg, self.COLOR)

class SyntaxNode(SyntaxNodeBase):
    """
    Defines a class for syntax only (i.e., a node not attached to a C++ class).

    This needs to be a separate class for type checking.
    """
    COLOR = 'GREEN'

    def markdown(self, prefix=''):
        """
        Return the expected markdown file name.
        """
        return os.path.join(prefix, self.fullpath.strip('/'), 'index.md')

    @property
    def parameters(self):
        """
        Return the action parameters for the syntax.
        """
        parameters = dict()
        for action in self.actions():
            if action.parameters is not None:
                parameters.update(action.parameters)
        return parameters

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        stub = self.STUB_HEADER
        stub += '\n# {} System\n'.format(self.name)
        stub += '!syntax objects {}\n\n'.format(self.fullpath)
        stub += '!syntax subsystems {}\n\n'.format(self.fullpath)
        stub += '!syntax actions {}\n'.format(self.fullpath)
        return stub

class ObjectNode(SyntaxNodeBase): #pylint: disable=abstract-method
    """
    Base class for nodes associated with C++ objects (Action, MooseObjectAction, or MooseObject).
    """
    def __init__(self, parent, name, item, **kwargs):
        SyntaxNodeBase.__init__(self, parent, name, **kwargs)
        self.__description = item['description']
        self.__parameters = item['parameters']

        self._locateGroupNames(item)
        if 'tasks' in item:
            for values in item['tasks'].itervalues():
                self._locateGroupNames(values)

    @property
    def description(self):
        """
        Return the object description.
        """
        return self.__description

    @property
    def parameters(self):
        """
        Return the object parameters.
        """
        return self.__parameters

    def markdown(self):
        """
        The expected markdown file.
        """
        return self.fullpath.strip('/') + '.md'

    def _locateGroupNames(self, item):
        """
        Creates a list of groups (i.e., Apps).
        """
        if 'file_info' in item:
            for info in item['file_info'].iterkeys():
                match = re.search(r'/(?P<group>\w+)(?:App|Syntax)\.C', info)
                if not match or (match and (match.group('group').lower() == 'moose')):
                     self._groups.add('Framework')
                else:
                    self._groups.add(match.group('group'))

class MooseObjectNode(ObjectNode):
    """
    MooseObject nodes.
    """
    COLOR = 'YELLOW'

    def __init__(self, parent, key, item, **kwargs):
        ObjectNode.__init__(self, parent, key, item, **kwargs)
        self.__class_name = item['class'] if 'class' in item else key

    @property
    def class_name(self):
        """
        Return the name of the C++ class, which can be different than the input file name.
        """
        return self.__class_name

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        template_filename = os.path.join(MooseDocs.MOOSE_DIR,
                                         'docs', 'templates', 'moose_object.md.template')
        with open(template_filename, 'r') as fid:
            template_content = fid.read()

        template_content = template_content.replace('FullPathCodeClassName',
                                                    '{}'.format(self.fullpath))
        template_content = template_content.replace('CodeClassName', '{}'.format(self.name))
        stub = self.STUB_HEADER
        stub += template_content
        return stub

class ActionNode(ObjectNode):
    """
    Action nodes.
    """
    COLOR = 'MAGENTA'

    @property
    def class_name(self):
        """
        Return the name of the C++ class for the action.
        """
        return self.name

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        template_filename = os.path.join(MooseDocs.MOOSE_DIR,
                                         'docs', 'templates',
                                         'action_object.md.template')
        with open(template_filename, 'r') as fid:
            template_content = fid.read()

        template_content = template_content.replace('FullPathCodeActionName',
                                                    '{}'.format(self.fullpath))
        template_content = template_content.replace('CodeActionName', '{}'.format(self.name))
        stub = self.STUB_HEADER
        stub += template_content
        return stub

class MooseObjectActionNode(ActionNode):
    """
    MooseObjectAction nodes.
    """
    COLOR = 'CYAN'
