#!/usr/bin/env python
import os
import re
import yaml
import collections

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print 'SLOW'
    from yaml import Loader, Dumper
from peacock.utils.ExeLauncher import runExe

MOOSE_REPOSITORY = 'github.com/idaholab/moose/blob/devel/'



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

        self._parameters = []
        self._column_widths = []
        for col in self.PARAMETER_TABLE_COLUMN_NAMES:
            self._column_widths.append(len(col))


    def addParam(self, param):

        self._parameters.append(param)
        for i in range(len(self.PARAMETER_TABLE_COLUMNS)):
            self._column_widths[i] = max(self._column_widths[i], len(str(param[self.PARAMETER_TABLE_COLUMNS[i]])))


    def __str__(self):




        md = []

        s = self._buildFormatString(self.PARAMETER_TABLE_COLUMN_NAMES)

        frmt = '| ' + ' | '.join( ['{:<{}s}'] * (len(s)/2) ) + ' |'
        md += [frmt.format(*s)]

        md += ['']
        for i in range(len(self.PARAMETER_TABLE_COLUMN_NAMES)):
            md[-1] += '| ' + '-'*self._column_widths[i] + ' '
        md[-1] += '|'

        for param in self._parameters:
            text = []
            for key in self.PARAMETER_TABLE_COLUMNS:
                text.append(str(param[key]))
            s = self._buildFormatString(text)
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


class RegexDatabase(object):
    def __init__(self, ext, regex, path):

        self._database = dict()

        for root, dirs, files in os.walk(path, topdown=False):
            for filename in files:
                if filename.endswith(ext):
                    full_file = os.path.join(root, filename)
                    fid = open(full_file, 'r')
                    content = fid.read()
                    fid.close()

                    for match in re.finditer(regex, content):
                        grp1 = match.group(1)
                        if grp1 not in self._database:
                            self._database[grp1] = []

                        rel = full_file.split('/moose/')[-1]
                        repo = MOOSE_REPOSITORY + rel

                        self._database[grp1].append( (rel, repo) )


    def __getitem__(self, key):
        return self._database[key]

    def markdown(self, key):
        input = self[key]

        md = []
        for rel, repo in input:
            md += ['* [{}]({})'.format(rel, repo)]
        return '\n'.join(md)




class InputFileDatabase(RegexDatabase):
    def __init__(self, path):
        RegexDatabase.__init__(self, '.i', r'type\s*=\s*(\w+)\b', path)

class ChildClassDatabase(RegexDatabase):
    def __init__(self, path):
        RegexDatabase.__init__(self, '.h', r'public\s*(\w+)\b', path)


if __name__ == '__main__':

    db = InputFileDatabase(os.path.join(os.environ['MOOSE_DIR'], 'tutorials'))
    tutorials = db.markdown('Diffusion')

    db = ChildClassDatabase(os.path.join(os.environ['MOOSE_DIR'], 'examples'))
    children = db.markdown('Diffusion')
    print children


    """
    app = os.path.join(os.environ['MOOSE_DIR'], 'test', 'moose_test-oprof')
    args = '--yaml'
    raw = runExe(app, args)

    ydata = YamlData(raw)

    path = '/Kernels/Diffusion'
    info = MooseObjectInformation(ydata[path])

    print info
    """
