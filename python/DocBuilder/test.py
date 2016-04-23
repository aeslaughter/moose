#!/usr/bin/env python
import os
import yaml
import collections
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print 'SLOW'
    from yaml import Loader, Dumper
from peacock.utils.ExeLauncher import runExe

class YamlData(object):
    def __init__(self, raw):
        raw = raw.split('**START YAML DATA**\n')[1]
        raw = raw.split('**END YAML DATA**')[0]
        self._data = yaml.load(raw, Loader=Loader)

    def __getitem__(self, key):
        for iter in self._data:
            result = self._search(key, iter)
            if result:
                return result

    @staticmethod
    def _search(key, data):
        if data['name'].endswith(key):
            return data

        if not data['subblocks']:
            return None

        for child in data['subblocks']:
            child_data = YamlData._search(key, child)
            if child_data:
                return child_data
        return None

class MooseObjectParameterTable(object):

    PARAMETER_TABLE_COLUMNS = ['name', 'required', 'cpp_type', 'description']
    PARAMETER_TABLE_COLUMN_NAMES = ['Name', 'Required', 'Type', 'Description']

    def __init__(self):

        self._column_widths = [0]*len(self.PARAMETER_TABLE_COLUMNS)


    def addParam(self, param):

        for i in range(len(self.PARAMETER_TABLE_COLUMNS)):
            self._column_widths[i] = max(self._column_widths[i], len(str(param[self.PARAMETER_TABLE_COLUMNS[i]])))


    def __str__(self):




        md = []

        s = self._buildFormatString(self.PARAMETER_TABLE_COLUMN_NAMES)

        frmt = '| ' + ' | '.join( ['{:<{}s}'] * (len(s)/2) ) + ' |'
        md += [frmt.format(*s)]

        return '\n'.join(md)

    def _buildFormatString(self, text):
        output = []
        for i in range(len(text)):
            output.append(text[i])
            output.append(self._column_widths[i])
        return output


class MooseObjectInformation(object):


    def __init__(self, yaml):

        self._class_name = yaml['name'].split('/')[-1]
        self._class_description = yaml['description']


        self._tables = collections.OrderedDict()
        for param in yaml['parameters']:
            name = param['group_name']
            if not name:
                name = 'General'

            if name not in self._tables:
                self._tables[name] = MooseObjectParameterTable()

            self._tables[name].addParam(param)

    def __str__(self):

        # Build a list of strings to be separated by '\n'
        md = []

        # The class title
        md += ['# {}'.format(self._class_name)]
        md += ['']

        # The class description
        md += ['## Class Description']
        md += [self._class_description]
        md += ['']

        # Print the InputParameter tables
        md += ['## Input Parameters']
        for name, table in self._tables.iteritems():
            md += ['### {} Parameters'.format(name)]
            md += [str(table)]
            md += ['']

        return '\n'.join(md)


if __name__ == '__main__':

    app = os.path.join(os.environ['MOOSE_DIR'], 'test', 'moose_test-oprof')
    args = '--yaml'
    raw = runExe(app, args)

    ydata = YamlData(raw)

    path = '/Kernels/Diffusion'
    info = MooseObjectInformation(ydata[path])

    print info




    """
    md = []
    md += ['# ' + path.split('/')[-1] ]
    md += ['## Class Description']
    md += [info['description']]

    columns = ['name', 'required', 'cpp_type', 'description']
    max_widths = [0, 0, 0, 0]
    widths = dict()
    groups = dict()
    for param in info['parameters']:
        name = param['group_name']

        if not name:
            name = ''

        if name not in widths:
            widths[name] = dict(zip(columns, max_widths))


        if name not in groups:
            groups[name] = []

        groups[name].append(param)

        for col in columns:
            widths[name][col] = max(len(str(param[col.lower()])), widths[name][col])

    print widths
    md += ['## Input Parameters'] # TODO: link to InputParameters md
    def markdownTable(param):

        md = ['']

        name = param['group_name']
        if not name:
            md += ['### Parameters']
        else:
            md += ['### ' + name + ' Parameters']

        md += ['', '']
        for c in columns:
            md[-2] += ' | ' + c
        md[-2] += ' |'
        md[-2] = md[-1].strip()
        print '\n'.join(md)

        #md += '| ' + param['variable'] + ' | ' + ''

    for key, group in groups.iteritems():
        for param in group:
            markdownTable(param)

    print '\n'.join(md)
    """
