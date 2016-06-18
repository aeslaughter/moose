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

    def _configure(self):

        with open(self._config_file, 'r') as fid:
            yml = yaml_load(fid.read())

        build_dir = yml.get('build_dir', 'docs/documentation')
        docs_dir = yml.get('docs_dir', '.')
        hide = yml.get('hide', dict())
        links = yml.get('link', dict())

        def init(cname):
            with open(cname) as fid:
                config = yaml_load(fid.read())

            config['build_dir'] = build_dir
            config['source_dir'] = os.path.dirname(cname)

            config.setdefault('docs_dir', docs_dir)
            config.setdefault('details_dir', 'docs/details')
            config.setdefault('repo', None)
            config.setdefault('doxygen', None)
            config.setdefault('hide', dict())
            config.setdefault('links', dict())

            config['hide'].update(hide)
            config['links'].update(links)

            return config

        #TODO: Error chech for 'extra' and 'include'

        configs = []
        for include in yml['extra']['include']:
            path = os.path.join(self._root, include, 'config.yml')
            configs.append(init(path))
        return configs


    def _generate(self):

        # Some arguments to be passed in
        dirname = os.path.join(self._root)

        # Setup the location
        log.info('Generating Documentation: {}'.format(config_file))

        # Parse the configuration file for the desired paths
        os.chdir(dirname)
        configs = self._configure()

        # Locate and run the MOOSE executable
        raw = runExe(exe, '--yaml')
        ydata = utils.MooseYaml(raw)
        import pprint
        for config in configs:
            generator = MooseDocs.MooseApplicationDocGenerator(ydata, config)
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
