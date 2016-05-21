#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import MooseDocs
import errno

#TODO: Make this a generic function in /moose/python/utils
from peacock.utils.ExeLauncher import runExe

class DatabaseItem(object):
    def __init__(self, filename):
        self._filename = filename

    def keys(self):
        pass

    def markdown(self):
        pass

    def content(self):
        fid = open(self._filename, 'r')
        content = fid.read()
        fid.close()
        return content


class MarkdownIncludeItem(DatabaseItem):

    def keys(self):
        yield os.path.basename(self._filename)[0:-3]

    def markdown(self):
        return '{{!{}!}}'.format(self._filename)

class RegexItem(DatabaseItem):

    def __init__(self, filename, regex):
        DatabaseItem.__init__(self, filename)
        self._regex = re.compile(regex)

    def keys(self):

        for match in re.finditer(self._regex, self.content()):
            grp1 = match.group(1)
            self._rel_path = self._filename.split('/moose/')[-1]
            self._repo = MooseDocs.MOOSE_REPOSITORY + self._rel_path
            yield grp1


#            self._database[grp1].append( (rel, repo, filename) )


class InputFileItem(RegexItem):
    def __init__(self, filename):
        RegexItem.__init__(self, filename, r'type\s*=\s*(\w+)\b')

    def markdown(self):
        return '* [{}]({})'.format(self._rel_path, self._repo)

class ChildClassItem(RegexItem):
    def __init__(self, filename):
        RegexItem.__init__(self, filename, r'public\s*(\w+)\b')

    def markdown(self):
        # Check for C file
        c_rel_path = self._rel_path.replace('/include/', '/src/').replace('.h', '.C')
        c_repo = self._repo.replace('/include/', '/src/').replace('.h', '.C')
        c_filename = self._filename.replace('/include/', '/src/').replace('.h', '.C')

        if os.path.exists(c_filename):
            md = '* [{}]({})\n[{}]({})'.format(self._rel_path, self._repo, c_rel_path, c_repo)
        else:
            md = '* [{}]({})'.format(self._rel_path, self._repo)

        return md

class Database(object):
    def __init__(self, ext, path, itype):
        self._database = dict()
        self._itype = itype

        for root, dirs, files in os.walk(path, topdown=False):
            for filename in files:
                if filename.endswith(ext):
                    self.update(os.path.join(root, filename))

    def update(self, filename):
        item = self._itype(filename)
        keys = item.keys()
        if keys:
            for key in keys:
                if key not in self._database:
                    self._database[key] = []
                self._database[key].append(item)

    def __getitem__(self, key):
        return self._database[key]

class MooseObjectInformation(object):
    """


    """



    def __init__(self, yaml, details, items, **kwargs):

        prefix = kwargs.pop('prefix', '')

        # Extract basic name and description from yaml data
        self._class_path = os.path.join(MooseDocs.MOOSE_DOCS_DIR, prefix) + str(yaml['name'])

        self._class_name = yaml['name'].split('/')[-1]
        self._class_description = yaml['description']
        self._class_details = details
        self._items = items

        self._tables = collections.OrderedDict()
        for param in yaml['parameters']:
            name = param['group_name']
            if not name and param['required']:
                name = 'Required'
            elif not name and not param['required']:
                name = 'Optional'

            if name not in self._tables:
                self._tables[name] = MooseDocs.parsing.MooseObjectParameterTable()

            self._tables[name].addParam(param)

    def __str__(self):
        return self.markdown()

    def write(self):

        dir_name = os.path.dirname(self._class_path)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        fid = open(self._class_path + '.md', 'w')
        fid.write(self.markdown())
        fid.close()

    def markdown(self):

        # Build a list of strings to be separated by '\n'
        md = []

        # The class title
        md += ['# {}'.format(self._class_name)]
        md += ['']

        # The class description
        #md += ['## Class Description']
        md += [self._class_description]
        md += ['']

        # The details
        for detail in self._class_details:
            md += [detail.markdown()]
            md += ['']

        # Re-order the table to insert 'Required' and 'Optional' first
        tables = collections.OrderedDict()
        keys = ['Required', 'Optional']
        for k in keys:
            if k in self._tables:
                tables[k] = self._tables.pop(k)
        for k, t in self._tables.iteritems():
            tables[k] = t

        # Print the InputParameter tables
        md += ['## Input Parameters']
        for name, table in tables.iteritems():
            md += ['### {} Parameters'.format(name)]
            md += [table.markdown()]
            md += ['']

        # Print the item information
        for key, item in self._items.iteritems():
            md += ['## {}'.format(key)]
            for k, i in item.iteritems():
                md += ['### {}'.format(k)]
                for j in i:
                    md += [j.markdown()]
                md += ['']
            md += ['']
        return '\n'.join(md)



if __name__ == '__main__':

    #TODO: Add 'moose_base' to yaml
    inputs = collections.OrderedDict()
    children = collections.OrderedDict()

    #details = MooseObjectMarkdownDatabase(os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'include'))
    # print db['Diffusion']

    details = Database('.md', os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'include'), MarkdownIncludeItem)
   # print details

    inputs['Tutorials'] = Database('.i', os.path.join(MooseDocs.MOOSE_DIR, 'tutorials'), InputFileItem)
    inputs['Examples'] = Database('.i', os.path.join(MooseDocs.MOOSE_DIR, 'examples'), InputFileItem)
    inputs['Tests'] = Database('.i', os.path.join(MooseDocs.MOOSE_DIR, 'test', 'tests'), InputFileItem)

    children['Tutorials'] = Database('.h', os.path.join(MooseDocs.MOOSE_DIR, 'tutorials'), ChildClassItem)
    children['Examples'] = Database('.h', os.path.join(MooseDocs.MOOSE_DIR, 'examples'), ChildClassItem)
    children['Tests'] = Database('.h', os.path.join(MooseDocs.MOOSE_DIR, 'test', 'include'), ChildClassItem)

    # Locate the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'test'), name='moose_test')
    #if isinstance(exe, int):
    #    print os.strerror(exe)

    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)

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


    info = MooseObjectInformation(ydata[path], details[name], items, prefix='framework')
    info.write()
