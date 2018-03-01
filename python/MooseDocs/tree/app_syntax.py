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
import sys
import collections
import logging

import anytree
import json

import mooseutils


from build_page_tree import build_regex, find_files
from MooseDocs.tree.syntax import SyntaxNode, MooseObjectNode, ActionNode, MooseObjectActionNode

LOG = logging.getLogger(__name__)


REGISTER_PAIRS = [('Postprocessor', 'UserObjects/*'),
                  ('AuxKernel', 'Bounds/*')]

REMOVE = ['/Variables/InitialCondition/*',
          '/AuxVariables/InitialCondition/*',
          '/Bounds',
          '/Bounds/*']

def __add_moose_object_helper(parent, name, item):
    """
    Helper to handle the Postprocessor/UserObject and Bounds/AuxKernel special case.
    """
    node = MooseObjectNode(parent, name, item)

    for base, parent_syntax in REGISTER_PAIRS:
        if ('moose_base' in item) and (item['moose_base'] == base) and \
           (item['parent_syntax'] == parent_syntax):
            node.parent = None

def __syntax_tree_helper(parent, item):
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
                MooseObjectActionNode(parent, key, action)
            else:
                ActionNode(parent, key, action)

    if 'star' in item:
        __syntax_tree_helper(parent, item['star'])

    if ('types' in item) and item['types']:
        for key, obj in item['types'].iteritems():
            __add_moose_object_helper(parent, key, obj)

    if ('subblocks' in item) and item['subblocks']:
        for k, v in item['subblocks'].iteritems():
            node = SyntaxNode(parent, k)
            __syntax_tree_helper(node, v)

    if ('subblock_types' in item) and item['subblock_types']:
        for k, v in item['subblock_types'].iteritems():
            __add_moose_object_helper(parent, k, v)


def app_syntax(exe, remove=None, remove_test_apps=True, hide=None):
    """
    Creates a tree structure representing the MooseApp syntax for the given executable.

    Inputs:
        location[str]: The folder to locate Moose executable.
        hide[dict]: Items to consider "hidden".
    """
    try:
        raw = mooseutils.runExe(exe, ['--json', '--allow-test-objects'])
        raw = raw.split('**START JSON DATA**\n')[1]
        raw = raw.split('**END JSON DATA**')[0]
        tree = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    except Exception: #pylint: disable=broad-except
        LOG.error("Failed to execute the MOOSE executable: %s", exe)
        sys.exit(1)

    root = SyntaxNode(None, '')
    for key, value in tree['blocks'].iteritems():
        node = SyntaxNode(root, key)
        __syntax_tree_helper(node, value)

    if remove is None:
        remove = REMOVE
    if remove is not None:
        exclude = []
        include = []
        for item in remove:
            if item.startswith('!'):
                include.append(item[1:])
            else:
                exclude.append(item)

        complete = set()
        for node in anytree.PreOrderIter(root):
            complete.add(node.fullpath)

        # Create the complete set of files
        output = set()
        for pattern in exclude:
            output.update(find_files(complete, pattern))

        for pattern in include:
            output -= find_files(output, pattern)

        complete -= output

        for node in anytree.PreOrderIter(root):
            if node.fullpath not in complete:
                node.parent = None

    if remove_test_apps:
        for node in anytree.PreOrderIter(root):
            if all([group.endswith('Test') for group in node.groups]):
                node.parent = None

    #if remove is not None:
    #    for node in root.findall():
    #       if node.

    """
    if hide is not None:
        for node in root.findall():
            if ('all' in hide) and (node.full_name in hide['all']):
                node.hidden = True
            for group in node.groups:
                if (group in hide) and (node.full_name in hide[group]):
                    node.hidden = True
    """
    return root
