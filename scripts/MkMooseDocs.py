#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import yaml
import logging

from mkdocs.utils import yaml_load

#TODO: Make this a generic function in /moose/python/utils
#from peacock.utils.ExeLauncher import runExe
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



class MooseApplicationDocGenerator(object):

    log = logging.getLogger('MkMooseDocs.MooseApplicationDocGenerator')

    def __init__(self, yaml_data, filename, source):



        # Read the supplied files
        self._yaml_data = yaml_data
        self._syntax = MooseDocs.MooseApplicationSyntax(yaml_data, *source)


        #self._objects = []
        self._systems = []
        for system in self._syntax.systems():
            self._systems.append(MooseDocs.MooseSystemInformation(yaml_data[system], self._syntax.getMarkdown(system)))


        self.buildYaml(filename)




    def write(self):

        for system in self._systems:
            system.write()



    def buildYaml(self, filename):
        """
        Generates the System.yml file.
        """

        def sub(syntax, key, node, level=0):
            """
            Function for generating yaml entries.
            """


            ynode = self._yaml_data[node['key']]


            if len(node.keys()) > 1:
                msg = '{}- {}:'.format(' '*4*level, key)
                self.log.debug(msg)
                yield msg

                if syntax.hasSyntax(key):
                    msg = '{}- {}: {}.md'.format(' '*4*(level+1), 'Overview', key)
                    self.log.debug(msg)
                    yield msg

            elif key != '*':
                msg = '{0}- {1}: {1}.md'.format(' '*4*level, key)
                self.log.debug(msg)
                yield msg


            for k, v in node.iteritems():
                if k != 'key':
                    sub(syntax, v, k, level+1)

            if ynode != None:
                if ynode['subblocks'] != None:
                    for child in ynode['subblocks']:
                        name = child['name'].split('/')[-1]
                        if name in syntax._objects:
                            msg = '{0}- {1}: {1}.md'.format(' '*4*(level+1), name)
                            self.log.debug(msg)
                            yield msg

        self.log.info('Creating YAML file: {}'.format(filename))
        output = []
        for key, value in self._syntax.syntax().iteritems():
            output += sub(self._syntax, key, value)

        fid = open(filename, 'w')
        fid.write('\n'.join(output))
        fid.close()





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
    config_file = os.path.join(dirname, 'mkdocs.yml')
    log.info('Generating documentation: {}'.format(config_file))

    # Parse the configuration file for the desired paths
    os.chdir(dirname)
    fid = open(config_file, 'r')
    config = yaml_load(fid.read())
    fid.close()

    # Extract the input/source link directories to utilize and build databases
    inputs = collections.OrderedDict()
    source = collections.OrderedDict()
    for key, value in config['extra']['Links'].iteritems():
        inputs[key] = MooseDocs.database.Database('.i', value, MooseDocs.database.items.InputFileItem)
        source[key] = MooseDocs.database.Database('.h', value, MooseDocs.database.items.ChildClassItem)

    # Locate and run the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'phase_field'), name='phase_field')
    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)


    for value in config['extra']['Generate'].values():
        generator = MooseApplicationDocGenerator(ydata, value['yaml'], value['source'])
        generator.write()

    """
    node = ydata['/Kernels']
    info = MooseDocs.MooseSystemInformation(node)
    info.write()
    """

    """
    path = '/Kernels/Diffusion'
    details = '/Users/slauae/projects/moose-doc/framework/include/kernels/Diffusion.md'
    info = MooseDocs.MooseObjectInformation(ydata[path], details, inputs=inputs, source=source)
    info.write()
    """
