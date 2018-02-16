"""Developer tools for MooseDocs."""
import os
import sys
import re
import importlib
import logging

import MooseDocs
from moosedown.tree import app_syntax

LOG = logging.getLogger(__name__)

def command_line_options(subparser):
    """Define the 'check' command."""
    devel_parser = subparser.add_parser('check', help='Syntax checking tools for MooseDocs.')

def main(options):

    location = os.path.join(MooseDocs.MOOSE_DIR, 'test')

    root = app_syntax(location)

    print root
