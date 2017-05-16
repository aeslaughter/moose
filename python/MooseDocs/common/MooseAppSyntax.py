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
import re
import collections
import pickle
import logging
import json

import anytree

import mooseutils
import MooseDocs

LOG = logging.getLogger(__name__)

class NodeBase(anytree.NodeMixin):
    """
    Node for MOOSE syntax that serves as the parent for actions/objects.
    """
    COLOR = 'RESET'
    STUB_HEADER = '<!-- MOOSE Documentation Stub: Remove this when content is added. -->\n'

    def __init__(self, name, parent=None):
        super(NodeBase, self).__init__()
        self.parent = parent
        self.name = name
        self.__hidden = False

    @property
    def full_name(self):
        """
        Return the MOOSE input file syntax for the node.
        """
        if self.parent:
            return '/'.join([self.parent.full_name, self.name])
        else:
            return self.name

    @property
    def groups(self):
        """
        Return the groups for the child actions (i.e., where the syntax is defined).
        """
        out = dict()
        for node in self.children:
            if isinstance(node, ActionNode):
                out.update(node.groups)
        return out

    @property
    def hidden(self):
        """
        Return the hidden status of the node.
        """
        return self.__hidden

    @hidden.setter
    def hidden(self, value):
        """
        Set the hidden status for the node.
        """
        self.__hidden = value
        for node in self.children:
            node.hidden = value

    def syntax(self, group=None):
        """
        Return the child syntax nodes.
        """
        return [node for node in self.children if isinstance(node, SyntaxNode) and \
                (group is None or group in node.groups)]

    def objects(self, group=None):
        """
        Return the groups for the child actions (i.e., where the syntax is defined).
        """
        return [node for node in self.children if isinstance(node, MooseObjectNode) and \
                (group is None or group in node.groups)]

    def actions(self, group=None):
        """
        Return the groups for the child actions (i.e., where the syntax is defined).
        """
        return [node for node in self.children if isinstance(node, ActionNode) and \
                (group is None or group in node.groups)]

    def markdown(self, install):
        """
        Return the expected markdown file name.
        """
        pass

    def check(self, install, generate=False):
        """
        Check that the expected documentation exists.
        """
        if not self.hidden:
            filename = self.markdown(install)
            if not os.path.exists(filename):
                LOG.error("No documentation for %s, documentation for this object should be "
                          "created in: %s", self.full_name, filename)
                if generate:
                    if not os.path.exists(os.path.dirname(filename)):
                        os.makedirs(os.path.dirname(filename))
                    LOG.info('Creating stub page for MOOSE action %s %s', self.full_name, filename)
                    with open(filename, 'w') as fid:
                        fid.write(self._defaultContent())
            else:
                with open(filename, 'r') as fid:
                    lines = fid.readlines()
                if self.STUB_HEADER in lines[0]:
                    LOG.error("A MOOSE generated stub page for %s exists, but no content was "
                              "added. Add documentation content to %s.", self.name, filename)

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        pass

    def __repr__(self):
        """
        Print the node name.
        """
        oname = self.__class__.__name__[:-4]
        msg = '{}: {} hidden={} groups={}'.format(oname,
                                                  str(self.full_name),
                                                  self.hidden,
                                                  self.groups.keys())
        return mooseutils.colorText(msg, self.COLOR)

    def __str__(self):
        """
        Calling print on this object will print the tree nice and pretty.
        """
        return str(anytree.RenderTree(self))

class SyntaxNode(NodeBase):
    """
    Defines a class for syntax only (i.e., a node not attached to a C++ class).

    This needs to be a separate class for type checking.
    """
    COLOR = 'GREEN'

    def markdown(self, install):
        """
        Return the expected markdown file name.
        """
        path = os.path.join(install, self.full_name.strip('/')).split('/')
        path += ['index.md']
        return MooseDocs.abspath('/'.join(path))

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        stub = self.STUB_HEADER
        stub += '\n# {} System\n'.format(self.name)
        stub += '!syntax parameters {}\n\n'.format(self.full_name)
        stub += '!syntax objects {}\n\n'.format(self.full_name)
        stub += '!syntax actions {}\n\n'.format(self.full_name)
        stub += '!syntax subsystems {}\n\n'.format(self.full_name)
        return stub


class MooseNodeBase(NodeBase):
    """
    Base class for nodes associated with objects (Action, MooseObjectAction, or MooseObject).
    """
    def __init__(self, name, item, parent=None):
        super(MooseNodeBase, self).__init__(name, parent)
        self.__description = item['description']
        self.__parameters = item['parameters']
        self.__groups = dict()

        if 'tasks' in item:
            for values in item['tasks'].itervalues():
                self._locateGroupNames(values)
        else:
            self._locateGroupNames(item)

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

    @property
    def groups(self):
        """
        The groups that this node is associated.
        """
        return self.__groups

    def markdown(self, install):
        """
        The expected markdown file.
        """
        folder = self.__groups.keys()[0]
        path = os.path.join(install, self.full_name.strip('/')).split('/')
        path.insert(-1, folder)
        return MooseDocs.abspath('/'.join(path) + '.md')

    def _locateGroupNames(self, item):
        """
        Creates a list of groups (i.e., Apps).
        """
        if 'file_info' in item:
            for info in item['file_info'].iterkeys():
                filename = info.replace('//', '/')
                if filename.startswith(os.path.join(MooseDocs.MOOSE_DIR, 'framework')):
                    self.__groups['framework'] = 'Framework'
                else:
                    match = re.search(r'/(?P<group>\w+)App\.C', filename)
                    if match:
                        heading = re.sub(r'(?<=[a-z])([A-Z])', r' \1', match.group('group'))
                        folder = heading.replace(' ', '_').lower()
                        self.__groups[folder] = heading

    def _defaultContent(self):
        """
        Markdown stub content.
        """
        stub = self.STUB_HEADER
        stub += '\n# {}\n'.format(self.name)
        stub += '!syntax description {}\n\n'.format(self.full_name)
        stub += '!syntax parameters {}\n\n'.format(self.full_name)
        stub += '!syntax objects {}\n\n'.format(self.full_name)
        stub += '!syntax inputs {}\n\n'.format(self.full_name)
        stub += '!syntax children {}\n\n'.format(self.full_name)
        return stub


class MooseObjectNode(MooseNodeBase):
    """
    MooseObject nodes.
    """
    COLOR = 'YELLOW'

    def __init__(self, key, item, parent=None):
        super(MooseObjectNode, self).__init__(key, item, parent)
        self.__class_name = item['class'] if 'class' in item else key

    @property
    def class_name(self):
        """
        Return the name of the C++ class, which can be different than the input file name.
        """
        return self.__class_name

class ActionNode(MooseNodeBase):
    """
    Action nodes.
    """
    COLOR = 'MAGENTA'

class MooseObjectActionNode(ActionNode):
    """
    MooseObjectAction nodes.
    """
    COLOR = 'CYAN'

class MooseAppSyntax(object):
    """
    Class for building complete MooseApp syntax tree.
    """
    def __init__(self, location, hide=None):

        exe = mooseutils.find_moose_executable(location)
        cache = os.path.join(MooseDocs.TEMP_DIR, 'moosedocs.json')

        if os.path.exists(cache) and (os.path.getmtime(cache) >= os.path.getmtime(exe)):
            with open(cache, 'r') as fid:
                LOG.debug('Reading MooseDocs JSON Pickle: ' + cache)
                tree = pickle.load(fid)

        else:
            raw = mooseutils.runExe(exe, '--json')
            raw = raw.replace(u'**START JSON DATA**', '').replace(u'**END JSON DATA**', '')
            tree = json.loads(raw, object_pairs_hook=collections.OrderedDict)

            with open(cache, 'w') as fid:
                LOG.debug('Writing MooseDocs JSON Pickle: ' + cache)
                pickle.dump(tree, fid)

        self._root = SyntaxNode('')
        for key, value in tree['blocks'].iteritems():
            node = SyntaxNode(key, parent=self._root)
            self.__helper(value, node)

        if hide is not None:
            for group, hidden in hide.iteritems():
                gfilter = lambda n, grp=group: ((grp == 'all') or (grp in n.groups)) and \
                          any(n.full_name.startswith(h) for h in hidden)
                for node in self.findall(filter_=gfilter):
                    node.hidden = True

    def __str__(self):
        """
        Calling print on this object will print the tree nice and pretty.
        """
        return str(anytree.RenderTree(self._root))

    def __nonzero__(self):
        """
        Return True if this class has nodes.
        """
        return len(self._root.children) > 0

    def findall(self, syntax='', filter_=None):
        """
        Locate all nodes that contain the supplied syntax.

        Args:
            syntax[str]: The desired syntax (i.e., node.syntax) to compare against.
            filter[function]: A filter function, if it returns true keep the node.
        """
        if filter_ is None:
            filter_ = lambda n: n.full_name.endswith(syntax)
        return [node for node in anytree.iterators.PreOrderIter(self._root, filter_=filter_)]

    def objects(self, syntax=''):
        """
        Locate all MooseObject nodes.

        Args:
            syntax[str]: The desired syntax (i.e., node.syntax) to compare against.
        """
        filter_ = lambda n: syntax in n.full_name and isinstance(n, MooseObjectNode)
        return self.findall(syntax, filter_=filter_)

    def actions(self, syntax=''):
        """
        Locate all Action or MooseObjectAction nodes.

        Args:
            syntax[str]: The desired syntax (i.e., node.syntax) to compare against.
        """
        filter_ = lambda n: syntax in n.full_name and \
                  isinstance(n, (ActionNode, MooseObjectActionNode))
        return self.findall(syntax, filter_=filter_)

    def syntax(self):
        """
        Return SyntaxNode objects.
        """
        filter_ = lambda n: isinstance(n, SyntaxNode) and (n is not self._root)
        return self.findall(filter_=filter_)

    def groups(self):
        """
        Return all the groups for this object.
        """
        out = dict()
        filter_ = lambda n: isinstance(n, (ActionNode, MooseObjectNode, MooseObjectActionNode))
        for node in anytree.iterators.PreOrderIter(self._root, filter_=filter_):
            out.update(node.groups)
        return out

    @staticmethod
    def __helper(item, parent):
        """
        Tree builder helper function.

        This investigates the JSON nodes and builds the proper input file tree for MooseDocs.
        """

        if item is None:
            return

        if 'actions' in item:
            for key, action in item['actions'].iteritems():
                if ('parameters' in action) and action['parameters'] and \
                ('isObjectAction' in action['parameters']):
                    MooseObjectActionNode(key, action, parent=parent)
                else:
                    ActionNode(key, action, parent=parent)

        if 'star' in item:
            MooseAppSyntax.__helper(item['star'], parent)

        if ('types' in item) and item['types']:
            for key, obj in item['types'].iteritems():
                MooseObjectNode(key, obj, parent=parent)

        if ('subblocks' in item) and item['subblocks']:
            for k, v in item['subblocks'].iteritems():
                node = SyntaxNode(k, parent=parent)
                MooseAppSyntax.__helper(v, node)

        if ('subblock_types' in item) and item['subblock_types']:
            for k, v in item['subblock_types'].iteritems():
                MooseObjectNode(k, v, parent=parent)
