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

    # Some arguments to be passed in
    dirname = os.path.join(MooseDocs.MOOSE_DIR, 'docs')

    # Setup the logger object
    log = logging.getLogger('MkMooseDocs')
    handler = logging.StreamHandler()
    formatter = MkMooseDocsFilter()#'%(name)s:%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    #log.setLevel(logging.DEBUG)

    # Setup the location
    config_file = os.path.join(dirname, 'config.yml')
    log.info('Generating Documentation: {}'.format(config_file))

    # Parse the configuration file for the desired paths
    os.chdir(dirname)
    fid = open(config_file, 'r')
    config = yaml_load(fid.read())
    fid.close()

    # Locate and run the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'phase_field'), name='phase_field')
    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)

    for value in config['generate'].values():
        generator = MooseDocs.MooseApplicationDocGenerator(ydata, value['prefix'], value['source'], links=config['links'], hide=config['hide'], details=value['details'])
        generator.write()

    """
    node = ydata['/Kernels']
    info = MooseDocs.MooseSystemInformation(node)
    info.write()
    """

    """
    path = '/Kernels/Diffusion'
    source = ['/Users/slauae/projects/moose-doc/framework/include/kernels/Diffusion.h']
    details = config['generate']['Framework']['details']
    info = MooseDocs.MooseObjectInformation(ydata.find(path), details, source)
    info.write(prefix='documentation/framework')
    """
