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




class MooseSystemInformation(object):

    def __init__(self, yaml, system):
        self._log = logging.getLogger(self.__class__.__name__)
        self._handler = logging.StreamHandler()
        self._log.setLevel(logging.ERROR)
        self._log.addHandler(self._handler)

        self._yaml = yaml


        self._system_node = self._yaml[system]


    def write(self):

        """
        dir_name = os.path.dirname(self._class_path)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        """


        fid = open('test.md', 'w')
        fid.write(self.markdown())
        fid.close()



    def markdown(self):

        md = []

        table = MooseDocs.MooseObjectParameterTable()

        if self._system_node['parameters']:
            for param in self._system_node['parameters']:
                table.addParam(param)

            md += ['## Input Parameters']
            md += [table.markdown()]



        if self._system_node['subblocks']:
            table = MooseDocs.MarkdownTable('Name', 'Description')
            for child in self._system_node['subblocks']:
                name = child['name']
                desc = child['description']


                if not desc:
                    self._log.error("{} object lacks a description.".format(name))


                table.addRow(name, desc)

            md += ['## Available Objects']
            md += [table.markdown()]

        return '\n'.join(md)

class MooseApplicationDocGenerator(object):
    def __init__(self, yaml_data, source):

        # Read the supplied files
        self._yaml_data = yaml_data
        #self._objects = []
        #self._systems = []

        print source, type(source)


        def gen(src, level=0):
            """
            Function for looping over supplied source directories.
            """
            for key, value in src.iteritems():
                yield '{}- {}:'.format(' '*4*level, key)
                if isinstance(value, dict):
                    out = gen(value, level+1)
                    yield '\n'.join(out)
                else:
                    syntax = MooseDocs.MooseApplicationSyntax(yaml_data, *value)
                    for k, v in syntax.syntax().iteritems():
                        out = self._sub(syntax, k, v, level+1)
                        yield '\n'.join(out)

        output = gen(source)
        print '\n'.join(output)




    def _sub(self, syntax, key, node, level=0):


        ynode = self._yaml_data[node['key']]#['subblocks']


        if len(node.keys()) > 1:
            yield '{}- {}:'.format(' '*4*level, key)
            yield '{}- {}: {}.md'.format(' '*4*(level+1), 'Overview', key)

        elif key != '*':
            yield '{0}- {1}: {1}.md'.format(' '*4*level, key)

        for k, v in node.iteritems():
            if k != 'key':
                self._sub(syntax, v, k, level+1)

        if ynode != None:
            if ynode['subblocks'] != None:
                for child in ynode['subblocks']:
                    name = child['name'].split('/')[-1]
                    if name in syntax._objects:
                        yield '{0}- {1}: {1}.md'.format(' '*4*(level+1), name)








if __name__ == '__main__':

    # Parse the configuration file for the desired paths
    os.chdir(os.path.join(MooseDocs.MOOSE_DIR, 'docs'))
    fid = open(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'mkdocs.yml'), 'r')
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




    generator = MooseApplicationDocGenerator(ydata, config['extra']['Source'])



   # Details = MooseDocs.database.Database('.md', include, MooseDocs.database.items.MarkdownIncludeItem)
    """
    path = '/Kernels/Diffusion'
    details = '/Users/slauae/projects/moose-doc/framework/include/kernels/Diffusion.md'
    info = MooseDocs.MooseObjectInformation(ydata[path], details, inputs=inputs, source=source)
    info.write()
    """
