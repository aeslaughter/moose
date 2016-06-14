import os
import collections
import logging

import MooseDocs
from MooseInformationBase import MooseInformationBase
from MooseObjectParameterTable import MooseObjectParameterTable


class MooseObjectInformation(MooseInformationBase):
    """
    Object for generating documentation for a MooseObject.

    Args:
        yaml: The YAML node for this object.


    """
    log = logging.getLogger('MkMooseDocs.MooseObjectInformation')

    def __init__(self, yaml, details, header, **kwargs):
        MooseInformationBase.__init__(self, yaml)

        #self._header = header
        #self._log = logging.getLogger(self.__class__.__name__)
        #self._handler = logging.StreamHandler()
        #self._log.setLevel(logging.INFO)
        #self._log.addHandler(self._handler)#

        #self._log.info('Initializing Documentation: {}'.format(yaml['name']))

        self._inputs = kwargs.pop('inputs', None)
        self._source = kwargs.pop('source', None)


        self._class_name = yaml['name'].split('/')[-1]
        #self._class_base = yaml['moosebase']
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

    @staticmethod
    def filename(name):
        return '{}.md'.format(name.strip('/').replace('/*', '').replace('/<type>', ''))

    def markdown(self):

        # Build a list of strings to be separated by '\n'
        md = []

        # The class title
        md += ['# {}'.format(self._class_name)]
        md += ['']

        # The class description
        if not self._class_description:
            self.log.error("{} object lacks a description.".format(self._class_name))
        else:
            md += [self._class_description]
            md += ['']

        # The details
        if self._class_details and os.path.exists(self._class_details):
            md += ['{{!{}!}}'.format(self._class_details)]
            md += ['']

        else:
            md += ['<p style="color:red;font-size:120%">']
            md += ['ERROR: Failed to located object detailed description: {}'.format(self._class_name)]
            md += ['</p>']
            self.log.error('Failed to load object description: {}'.format(self._class_name))


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
        md += ['* Source: [{}]({})'.format(self._class_name, self._source)]
        #md += ['* Moose System: {}'.format(self._class_base)]
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
        if items != None and len(items) > 0:
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
