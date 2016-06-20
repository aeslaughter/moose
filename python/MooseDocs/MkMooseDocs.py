#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import yaml
import logging

from mkdocs.utils import yaml_load

import subprocess

import MooseDocs
from MooseApplicationDocGenerator import MooseApplicationDocGenerator



class MkMooseDocsFilter(logging.Formatter):

    COLOR = {'DEBUG':'GREEN', 'INFO':'RESET', 'WARNING':'YELLOW', 'ERROR':'RED', 'CRITICAL':'MAGENTA'}

    def format(self, record):
        msg = logging.Formatter.format(self, record)

        indent = record.name.count('.')

        if record.levelname in ['WARNING', 'ERROR', 'CRITICAL']:
            msg = '{}{}: {}'.format(' '*4*indent, record.levelname, msg)
        else:
            msg = '{}{}'.format(' '*4*indent, msg)

        if record.levelname in self.COLOR:
            msg = utils.colorText(msg, self.COLOR[record.levelname])

        return msg

#TODO: Make this a generic function in /moose/python/utils
#from peacock.utils.ExeLauncher import runExe
def runExe(app_path, args):

    popen_args = [str(app_path)]
    if isinstance(args, str):
        popen_args.append(args)
    else:
        popen_args.extend(args)

    proc = subprocess.Popen(popen_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = proc.communicate()
    stdout_data = data[0].decode("utf-8")
    return stdout_data



if __name__ == '__main__':

    # Setup the logger object
    log = logging.getLogger('MkMooseDocs')
    handler = logging.StreamHandler()
    formatter = MkMooseDocsFilter()#'%(name)s:%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    #log.setLevel(logging.DEBUG)


    root = MooseDocs.MOOSE_DIR

    config_file = os.path.join('docs', 'mkdocs.yml')
    exe = utils.find_moose_executable(os.path.join(root, 'modules', 'phase_field'), name='phase_field')

    gen = MooseApplicationDocGenerator(root, config_file, exe)
    gen()
