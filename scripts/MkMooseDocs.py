#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import MooseDocs

import yaml
import logging

#TODO: Make this a generic function in /moose/python/utils
#from peacock.utils.ExeLauncher import runExe
import subprocess


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




class MooseObjectList(object):
    def __init__(self, yaml, path):
        self._yaml = yaml
        self._path = path

        self._moosebase = dict()
        def getdata(data):

            if 'moosebase' in data:
                m = data['moosebase']
                if m not in self._moosebase:
                    self._moosebase[m] = []
                self._moosebase[m].append(data['name'])

            if data['subblocks']:
                for child in data['subblocks']:
                    getdata(child)

        for itr in self._yaml.get():
            getdata(itr)


        self._syntax = set()
        self._register = dict()
        self._filenames = dict()


        # Walk the directory, looking for files with the supplied extension.
        for root, dirs, files in os.walk(path, topdown=False):
            for filename in files:


                if filename.endswith('.C') or filename.endswith('.h'):
                    fullfile = os.path.join(root, filename)

                    fid = open(fullfile, 'r')
                    content = fid.read()
                    fid.close()

                    for match in re.finditer(r'register\w+?\((?P<key>\w+)\);', content):
                        key = match.group('key')
                        self._register[key] = key

                    for match in re.finditer(r'registerNamed\w+?\((?P<class>\w+),\s*"(?P<key>\w+)"\);', content):
                        self._register[match.group('class')] = match.group('key')

                    if filename.endswith('.h'):
                        for match in re.finditer(r'class\s*(?P<class>\w+)', content):
                            self._filenames[match.group('class')] = fullfile

                    for match in re.finditer(r'registerActionSyntax\("(?P<action>\w+)"\s*,\s*"(?P<syntax>.*?)\"[,\);]', content):
                        self._syntax.add(match.group('syntax'))


    def syntax(self):
        """
        Return the syntax defined in the supplied applications.
        """
        return self._syntax




if __name__ == '__main__':


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

    yml = collections.defaultdict(dict)

    def attach(branch, trunk):

        a,b = branch.split('/', 1)
        trunk[a] = ''
        if b:
            attach(b, trunk[a])






    # USE TUPLES AS KEYS
    #yml[('Adaptivity', 'Markers', '*')] = 'Overview.md'
    #yml[('Adaptivity', 'Markers', 'BoxMarker')] = 'BoxMarker.md'
    #
    # Make a database of markdown files, so they can just go anywhere?

    objects = MooseObjectList(ydata, os.path.join(MooseDocs.MOOSE_DIR, 'framework'))
    for syntax in objects.syntax():

        attach(syntax, yml)

        #regex = r'(\w+)'
        #match = re.findall(r'(\w+)', s)
        #n = len(match)

        #if n == 1:
        #yml.append('- {}:'.format(match[0]))



        #for i in range(len(match)):
        #    key = '- {}'.format(match[i])
        #    yml[key] = ''
    print yml

    #with open('result.yml', 'w') as fid:
    #    fid.write('\n'.join(yml))
#        yaml.dump(yml, fid, default_flow_style=False)
        #print s, match

        #name = s.replace('*', '').strip('/').split('/')
        #print name


       # print ydata[s]['name'], ydata[s]['subblocks'] == None













    # Build databases (avoids excessive directory walking).
    framework = os.path.join(MooseDocs.MOOSE_DIR, 'framework')
    src = os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'src')
    include = os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'include')
    tutorials = os.path.join(MooseDocs.MOOSE_DIR, 'tutorials')
    examples = os.path.join(MooseDocs.MOOSE_DIR, 'examples')
    tests = os.path.join(MooseDocs.MOOSE_DIR, 'test')

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
