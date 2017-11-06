import os
import subprocess

BLOCK = 'block'
INLINE = 'inline'

ROOT_DIR = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                   cwd=os.getcwd(),
                                   stderr=subprocess.STDOUT).strip('\n')
