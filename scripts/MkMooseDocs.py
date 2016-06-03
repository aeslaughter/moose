#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import yaml
import logging

#TODO: Make this a generic function in /moose/python/utils
#from peacock.utils.ExeLauncher import runExe
import subprocess

import MooseDocs
from MooseApplicationSyntax import MooseApplicationSyntax


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








if __name__ == '__main__':


    # Build databases (avoids excessive directory walking).
    framework = os.path.join(MooseDocs.MOOSE_DIR, 'framework')
    phase_field = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'phase_field')


    src = os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'src')
    include = os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'include')
    tutorials = os.path.join(MooseDocs.MOOSE_DIR, 'tutorials')
    examples = os.path.join(MooseDocs.MOOSE_DIR, 'examples')
    tests = os.path.join(MooseDocs.MOOSE_DIR, 'test')




    # Locate the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'test'), name='moose_test')
    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)

    """
    system = MooseSystemInformation(ydata, 'Outputs')
    system.write()
    """


    # Loop over the syntax in the framework.
    #    (1) Generate the Systems yaml file.
    #    (2) Generate the System overview markdown files.
    #    (3) Generate the MooseObject markdown files.

    FILE_MARKER = 'key'

    yml = dict()

    def attach(branch, key, trunk):
        """
        Insert a branch of directories on its trunk.
        """

        parts = branch.split('/', 1)
        key = parts[0]

        if key not in trunk:
            trunk[key] = dict()
            trunk[key]['key'] = '{}/{}'.format(trunk['key'], key)

        if len(parts) == 2:
            node, others = parts
            attach(others, key, trunk[key])






    app_syntax = MooseSourceDirectory(ydata, framework, phase_field)

    for syntax in app_syntax.syntax():
        key = syntax.split('/')[0]
        if key not in yml:
            yml[key] = dict()
            yml[key]['key'] = '/{}'.format(key)
        attach(syntax, key, yml)

        #regex = r'(\w+)'
        #match = re.findall(r'(\w+)', s)
        #n = len(match)

        #if n == 1:
        #yml.append('- {}:'.format(match[0]))



        #for i in range(len(match)):
        #    key = '- {}'.format(match[i])
        #    yml[key] = ''

    print yml['Kernels']
    print yml['Adaptivity']

    #with open('result.yml', 'w') as fid:
    #    fid.write('\n'.join(yml))
#        yaml.dump(yml, fid, default_flow_style=False)
        #print s, match

        #name = s.replace('*', '').strip('/').split('/')
        #print name


       # print ydata[s]['name'], ydata[s]['subblocks'] == None













    #db = MooseDocs.database.Database('.C', src, MooseDocs.database.items.RegisterItem)
    #print db['ParsedFunction'][0].src()



 #   obj = MooseObjectList(ydata, framework)


    """
    inputs = collections.OrderedDict()
    children = collections.OrderedDict()

    details = MooseDocs.database.Database('.md', include, MooseDocs.database.items.MarkdownIncludeItem)

    inputs['Tutorials'] = MooseDocs.database.Database('.i', tutorials, MooseDocs.database.items.InputFileItem)
    inputs['Examples'] = MooseDocs.database.Database('.i', examples, MooseDocs.database.items.InputFileItem)
    inputs['Tests'] = MooseDocs.database.Database('.i', tests, MooseDocs.database.items.InputFileItem)

    children['Tutorials'] = MooseDocs.database.Database('.h', tutorials, MooseDocs.database.items.ChildClassItem)
    children['Examples'] = MooseDocs.database.Database('.h', examples, MooseDocs.database.items.ChildClassItem)
    children['Tests'] = MooseDocs.database.Database('.h', tests, MooseDocs.database.items.ChildClassItem)


    path = '/Kernels/Diffusion'
    name = 'Diffusion'

    input_header = 'Input File Use'
    child_header = 'Child Objects'

    items = collections.OrderedDict()
    items[input_header] = collections.OrderedDict()
    items[child_header] = collections.OrderedDict()

    for key, item in inputs.iteritems():
        items[input_header][key] = item[name]
    for key, item in children.iteritems():
        items[child_header][key] = item[name]

    info = MooseObjectInformation(ydata[path], details[name], items, prefix='MooseSystems')
    info.write()
    """
