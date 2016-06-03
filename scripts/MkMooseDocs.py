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
        self._log.setLevel(logging.DEBUG)
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
    def __init__(self, yaml_data, *args):

        # Read the supplied files
        self._yaml_data = yaml_data
        self._objects = []
        self._systems = []



        output = []
        for item in args:
            fname = item[0]

            level = 0
            for prefix in item[1]:
                output.append('{}- {}:'.format(' '*4*level, prefix))
                level += 1

            syntax = MooseDocs.MooseApplicationSyntax(yaml_data, fname)

            for key, value in syntax.syntax().iteritems():
                output += self._gen(syntax, value, key, level)

        print '\n'.join(output)





    def _gen(self, syntax, node, key, level=0):

        ynode = self._yaml_data[node['key']]#['subblocks']


        if len(node.keys()) > 1:
            yield '{}- {}:'.format(' '*4*level, key)
            yield '{}- {}: {}.md'.format(' '*4*(level+1), 'Overview', key)

        elif key != '*':
            yield '{0}- {1}: {1}.md'.format(' '*4*level, key)

        for k, v in node.iteritems():
            if k != 'key':
                self._gen(syntax, v, k, level+1)

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

    print config['extra']['Source']
    print config['extra']['Links']


    # Locate and run the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'phase_field'), name='phase_field')
    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)

    #generator = MooseApplicationDocGenerator(ydata, (framework, ['Framework']), (phase_field, ['Modules', 'Phase Field']))



   # details = MooseDocs.database.Database('.md', include, MooseDocs.database.items.MarkdownIncludeItem)


    inputs = collections.OrderedDict()
    children = collections.OrderedDict()
    for key, value in config['extra']['Links'].iteritems():
        inputs[key] = MooseDocs.database.Database('.i', value, MooseDocs.database.items.InputFileItem)
        children[key] = MooseDocs.database.Database('.h', value, MooseDocs.database.items.ChildClassItem)

    """

    inputs['Tutorials'] = MooseDocs.database.Database('.i', tutorials, MooseDocs.database.items.InputFileItem)
    inputs['Examples'] = MooseDocs.database.Database('.i', examples, MooseDocs.database.items.InputFileItem)
    inputs['Tests'] = MooseDocs.database.Database('.i', tests, MooseDocs.database.items.InputFileItem)

    children['Tutorials'] = MooseDocs.database.Database('.h', tutorials, MooseDocs.database.items.ChildClassItem)
    children['Examples'] = MooseDocs.database.Database('.h', examples, MooseDocs.database.items.ChildClassItem)
    children['Tests'] = MooseDocs.database.Database('.h', tests, MooseDocs.database.items.ChildClassItem)
    """

    path = '/Kernels/Diffusion'
    name = 'Diffusion'

    input_header = 'Input File Use'
    child_header = 'Child Objects'

    items = collections.OrderedDict()
    items[input_header] = collections.OrderedDict()
    items[child_header] = collections.OrderedDict()

    """
    for key, item in inputs.iteritems():
        if name in item:
            items[input_header][key] = item[name]
    for key, item in children.iteritems():
        if name in item:
            items[child_header][key] = item[name]
    """

    details = '/Users/slauae/projects/moose-doc/framework/include/kernels/Diffusion.md'
    info = MooseDocs.MooseObjectInformation(ydata[path], details, items)
    info.write()
