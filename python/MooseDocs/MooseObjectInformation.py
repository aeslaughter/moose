import os
import collections
import MooseDocs
from MooseObjectParameterTable import MooseObjectParameterTable

class MooseObjectInformation(object):
    """
    Object for generating documentation for a MooseObject.

    Args:
        yaml: The YAML node for this object.


    """



    def __init__(self, yaml, details, items, **kwargs):

        prefix = kwargs.pop('prefix', '')

        # Extract basic name and description from yaml data
        #self._class_path = os.path.join(MooseDocs.MOOSE_DOCS_DIR, prefix) + str(yaml['name'])

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
                self._tables[name] = MooseObjectParameterTable()

            self._tables[name].addParam(param)

    def __str__(self):
        return self.markdown()

    def write(self):

        dir_name = os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'gen')
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        print dir_name

        fid = open(os.path.join(dir_name, self._class_name + '.md'), 'w')
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
        md += ['{{!{}!}}'.format(self._class_details)]
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
