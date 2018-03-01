"""Developer tools for MooseDocs."""
import os
import sys
import re
import importlib
import logging

import anytree

import mooseutils

import MooseDocs
from MooseDocs.tree import app_syntax

LOG = logging.getLogger(__name__)


def _get_default_executable():
    locs = os.getcwd().replace(MooseDocs.ROOT_DIR, '').split('/')
    for i in range(len(locs), 0, -1):
        path = os.path.join(MooseDocs.ROOT_DIR, *locs[:i])
        exe = mooseutils.find_moose_executable(path, show_error=False)
        if exe:
            return exe

def _get_default_groups(exe):
    if exe:
        name = os.path.basename(exe).split('-')[0].replace('_', ' ').title().replace(' ', '')
        return [name, 'Framework']


def command_line_options(subparser, parent):
    """Define the 'check' command."""

    parser = subparser.add_parser('check',
                                  parents=[parent],
                                  help='Syntax checking tools for MooseDocs.')

    parser.add_argument('--executable', '-e', default=_get_default_executable(), type=str,
                        help="The executable to use for checking syntax documentation "
                             "(default: %(default)s).")
    parser.add_argument('--generate', action='store_true',
                        help="When checking the application for complete documentation generate "
                             "any missing markdown documentation files.")
    parser.add_argument('--update', action='store_true',
                        help="When checking the application for complete documentation generate "
                             "any missing markdown documentation files and update the stubs for "
                             "files that have not been modified.")
    parser.add_argument('--dump', action='store_true',
                        help="Dump the complete MooseDocs syntax tree to the screen.")
    parser.add_argument('--groups',
                        default=_get_default_groups(parser.get_default('executable')),
                        help="Specify the groups to consider in the check, by default only the "
                             "documentation for the application is considered, providing an empty "
                             "list will check all groups (default: %(default)s).")

def main(options):
    print options.executable, os.path.isfile(options.executable)

    root = app_syntax(options.executable)
    if options.dump:
        print root

    for node in anytree.PreOrderIter(root):
        node.check(generate=options.generate, update=options.update, groups=set(options.groups))
