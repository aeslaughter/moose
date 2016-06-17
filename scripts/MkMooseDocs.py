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


class MooseDocGenerator(object):
    """



    """

    def __init__(self, root, config_file, exe, **kwargs):

        self._root = root
        self._config_file = config_file
        self._exe = exe
        self._modified = None
        self._develop = kwargs.pop('develop', False)

    def __call__(self):

        modified = os.path.getmtime(self._exe)
        if self._modified != os.path.getmtime(self._exe):
            self._generate()
            self._modified = modified


    def _generate(self):

        # Some arguments to be passed in
        dirname = os.path.join(self._root)


        # Setup the location
        log.info('Generating Documentation: {}'.format(config_file))

        # Parse the configuration file for the desired paths
        os.chdir(dirname)
        fid = open(config_file, 'r')
        config = yaml_load(fid.read())['extra']
        fid.close()


        def setdefault(config):
            config.setdefault(u'docs_dir', 'docs')
            config.setdefault(u'build_dir', 'docs/documentation')
            config.setdefault(u'source_dir', '.')
            config.setdefault(u'details_dir', '.')
            config.setdefault(u'repo', None)
            config.setdefault(u'doxygen', None)

        # Locate and run the MOOSE executable
        raw = runExe(exe, '--yaml')
        ydata = utils.MooseYaml(raw)

        for value in config['generate'].values():
            setdefault(value)
            generator = MooseDocs.MooseApplicationDocGenerator(ydata, value, links=config['links'], hide=config['hide'])
            generator.write()

    """
    c = config['generate']['Framework']
    syntax = MooseDocs.MooseApplicationSyntax(ydata, path=c.get('path', '.'))
    """

    """
    node = ydata.find('/Kernels')
    c = config['generate']['Framework']
    setdefault(c)
    info = MooseDocs.MooseSystemInformation(node, **c)
    info.write()
    """

    """
    path = '/Kernels/Diffusion'
    source = ['framework/include/kernels/Diffusion.h']
    c = config['generate']['Framework']
    setdefault(c)
    info = MooseDocs.MooseObjectInformation(ydata.find(path), source, **c)
    info.write()
    """

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

    gen = MooseDocGenerator(root, config_file, exe)
    gen()
