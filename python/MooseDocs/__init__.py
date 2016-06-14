import extensions
import database

from MarkdownTable import MarkdownTable
from MooseObjectParameterTable import MooseObjectParameterTable
from MooseObjectInformation import MooseObjectInformation
from MooseSystemInformation import MooseSystemInformation
from MooseApplicationSyntax import MooseApplicationSyntax
from MooseApplicationDocGenerator import MooseApplicationDocGenerator

import os
MOOSE_REPOSITORY = 'https://github.com/idaholab/moose/blob/devel/'
MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getenv('HOME'), 'projects', 'moose'))
MOOSE_DOCS_DIR = os.path.join(MOOSE_DIR, 'docs', 'documentation')
MOOSE_DOXYGEN = 'http://mooseframework.com/docs/doxygen/moose/'

# Throw an exception if MOOSE_DIR is not found.
if not os.path.exists(MOOSE_DIR):
    raise Exception('The MOOSE directory was not located.')
