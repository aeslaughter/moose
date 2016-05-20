import extensions
import parsing

import os
MOOSE_REPOSITORY = 'https://github.com/idaholab/moose/blob/devel/'
MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getenv('HOME'), 'projects', 'moose'))
MOOSE_DOCS_DIR = os.path.join(MOOSE_DIR, 'docs', 'documentation')

# Throw an exception if MOOSE_DIR is not found.
if not os.path.exists(MOOSE_DIR):
    raise Exception('The MOOSE directory was not located.')
