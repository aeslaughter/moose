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

        # Read the general yml file (e.g. mkdocs.yml)
        with open(self._config_file, 'r') as fid:
            yml = yaml_load(fid.read())

        # Global Config settings (and defaults)
        global_config = yml['extra'].get('global_config', dict())
        global_config.setdefault('build', os.path.join(self._root, 'docs', 'documentation'))
        global_config.setdefault('details', os.path.join(self._root, 'docs', 'details'))
        global_config.setdefault('docs', os.path.join(self._root, 'docs'))
        global_config.setdefault('repo', None)
        global_config.setdefault('doxygen', None)
        global_config.setdefault('hide', list())
        global_config.setdefault('links', dict())

        def update_config(dirname, cname):
            """
            Helper for updating/creating local configuration dict.
            """

            # Open the local config file
            with open(cname) as fid:
                config = yaml_load(fid.read())

            # Set the default source directory
            global_config.setdefault('source', os.path.dirname(cname))

            # Set the defaults
            for key, value in global_config.iteritems():
                config.setdefault(key, value)

            # Append the hide/links data
            config['hide'] = set(config['hide'] + global_config['hide'])
            config['links'].update(global_config['links'])

            # Re-define the links path relative to working directory
            for key, value in config['links'].iteritems():
                out = []
                for path in value:
                    out.append(os.path.abspath(os.path.join(dirname, path)))
                config['links'][key] = out

            return config

        #TODO: Error chech for 'extra' and 'include'

        configs = []
        for include in yml['extra']['include']:
            path = os.path.join(self._root, include, 'config.yml')
            configs.append(update_config(include, path))
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

        for config in configs:
            generator = MooseDocs.MooseApplicationDocGenerator(ydata, config)
            generator.write()


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
