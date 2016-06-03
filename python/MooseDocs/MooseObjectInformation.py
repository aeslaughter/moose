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



    def __init__(self, yaml, details, **kwargs):

        self._inputs = kwargs.pop('inputs', None)
        self._source = kwargs.pop('source', None)


        self._class_name = yaml['name'].split('/')[-1]
        self._class_base = yaml['moosebase']
        self._class_description = yaml['description']
        self._class_details = details

        # Create the tables (generate 'Required' and 'Optional' initially so that they come out in the proper order)
        self._tables = collections.OrderedDict()
        self._tables['Required'] = MooseObjectParameterTable()
        self._tables['Optional'] = MooseObjectParameterTable()

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
        md += [self._class_description]
        md += ['']

        # The details
        md += ['{{!{}!}}'.format(self._class_details)]
        md += ['']

        # Print the InputParameter tables
        md += ['## Input Parameters']
        for name, table in self._tables.iteritems():
            if table.size() == 0:
                continue
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
        md += self._linkMarkdown('Input Files', self._inputs)
        md += self._linkMarkdown('Child Objects', self._source)

        return '\n'.join(md)

    def _linkMarkdown(self, title, items):
        """
        Helper method for dumping link lists. (static, protected)

        Args:
            title[str]: The title of the list.
            items[list]: The list of of DatabaseItem objects.
        """

        md = []
        if items != None:
            md += ['## {}'.format(title)]
            for k, db in items.iteritems():
                if self._class_name in db:
                    md += ['### {}'.format(k)]
                    md += ['<div style="max-height:350px;overflow-y:Scroll">\n']
                    for j in db[self._class_name]:
                        md += [j.markdown()]
                    md += ['\n</div>']
                    md += ['']
            md += ['']

        return md
