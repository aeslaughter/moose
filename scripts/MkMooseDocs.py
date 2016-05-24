#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import MooseDocs

#TODO: Make this a generic function in /moose/python/utils
from peacock.utils.ExeLauncher import runExe

class MooseObjectInformation(object):
    """


    """



    def __init__(self, yaml, details, items, **kwargs):

        prefix = kwargs.pop('prefix', '')

        # Extract basic name and description from yaml data
        self._class_path = os.path.join(MooseDocs.MOOSE_DOCS_DIR, prefix) + str(yaml['name'])

        self._class_name = yaml['name'].split('/')[-1]
        self._class_base = yaml['moosebase']
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

        # Developer information
        md += ['## Additional Developer Documentation']
        md += ['* Moose System: {}'.format(self._class_base)]
        md += ['* Class Doxygen: [{}]({})'.format(self._class_name,
                                          os.path.join(MooseDocs.MOOSE_DOXYGEN, 'class' + self._class_name + '.html'))]

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


    # Locate the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'test'), name='moose_test')
    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)

    mb = ydata.mooseBaseDict()
    print mb['Material']




    # Build databases (avoids excessive directory walking).
    src = os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'src')
    include = os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'include')
    tutorials = os.path.join(MooseDocs.MOOSE_DIR, 'tutorials')
    examples = os.path.join(MooseDocs.MOOSE_DIR, 'examples')
    tests = os.path.join(MooseDocs.MOOSE_DIR, 'test')

    db = MooseDocs.database.Database('.C', src, MooseDocs.database.items.RegisterItem)

  #  print db._database




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
