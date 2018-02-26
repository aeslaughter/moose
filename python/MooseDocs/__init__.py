import os
import subprocess
import logging

BLOCK = 'block'
INLINE = 'inline'

LOG_LEVEL = logging.NOTSET

ROOT_DIR = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                   cwd=os.getcwd(),
                                   stderr=subprocess.STDOUT).strip('\n')

MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getcwd(), '..', 'moose'))
if not os.path.exists(MOOSE_DIR):
    MOOSE_DIR = os.path.join(os.getenv('HOME'), 'projects', 'moose')

os.environ['MOOSE_DIR'] = MOOSE_DIR
os.environ['ROOT_DIR'] = ROOT_DIR

PROJECT_FILES = subprocess.check_output(['git', 'ls-files'], cwd=ROOT_DIR).split('\n')

import base
import extensions
