import os
import subprocess

import base
import extensions

BLOCK = 'block'
INLINE = 'inline'

ROOT_DIR = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                   cwd=os.getcwd(),
                                   stderr=subprocess.STDOUT).strip('\n')

MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getcwd(), '..', 'moose'))
if not os.path.exists(MOOSE_DIR):
    MOOSE_DIR = os.path.join(os.getenv('HOME'), 'projects', 'moose')

os.environ['MOOSE_DIR'] = MOOSE_DIR
os.environ['ROOT_DIR'] = ROOT_DIR
