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

from .base import NodeBase, Property

LOG = logging.getLogger(__name__)

class SyntaxNodeBase(NodeBase):
    """
    Node for MOOSE syntax that serves as the parent for actions/objects.
    """
    PROPERTIES = NodeBase.PROPERTIES + [Property('hidden', ptype=bool, default=False)]

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

    def check(self, install, generate=False, groups=None, update=None):
        """
        Check that the expected documentation exists.

        Return:
            True, False, or None, where True indicates that the page exists, False indicates the
            page does not exist or doesn't contain content, and None indicates that the page is
            hidden.
        """
        out = None # not checked because it was hidden
        if self.hidden:
            LOG.debug("Skipping documentation check for %s, it is hidden.", self.fullpath)

        elif groups and not set(self.groups).intersection(groups):
            LOG.debug("Skipping documentation check for %s (%s), it is not listed in the provided "
                      "groups: %s.", self.fullpath, self.groups.keys(), groups)

        else:
            filename = self.markdown(install)
            if not os.path.isfile(filename):
                out = False
                LOG.error("No documentation for %s, documentation for this object should be "
                          "created in: %s", self.fullpath, filename)
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
                with open(filename, 'r') as fid:
                    lines = fid.readlines()
                if lines and self.STUB_HEADER in lines[0]:
                    out = False
                    LOG.error("A MOOSE generated stub page for %s exists, but no content was "
                              "added. Add documentation content to %s.", self.name, filename)
                    if update:
                        LOG.info("Updating stub page for %s in file %s.", self.name, filename)
                        with open(filename, 'w') as fid:
                            content = self._defaultContent()
                            if not isinstance(content, str):
                                raise TypeError("The _defaultContent method must return a str.")
                            fid.write(content)
        return out

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


        #path = os.path.join(install, self.fullpath.strip('/')).split('/')
        #path += ['index.md']
        #if absolute:
        #    return os.path.join(self.root_directory, *path)
        #else:
        #    return os.path.join(*path)

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

    def markdown(self, prefix=''):
        """
        The expected markdown file.
        """
        return os.path.join(prefix, self.fullpath.strip('/') + '.md')

        # folder = self.__groups.keys()[0]
        # path = os.path.join(install, self.fullpath.strip('/')).split('/')
        # path.insert(-1, folder)
        # if absolute:
        #     return os.path.join(self.root_directory, '/'.join(path) + '.md')
        # else:
        #     return os.path.join(*path) + '.md'

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
                                         'docs/templates/standards/moose_object.md.template')
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
                                         'docs/templates/standards/'
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
