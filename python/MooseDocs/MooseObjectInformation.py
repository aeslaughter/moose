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

    def __init__(self, yaml, src, **kwargs):
        MooseInformationBase.__init__(self, yaml, **kwargs)

        self.log.info('Initializing Documentation: {}'.format(yaml['name']))

        self._src = src

        self._inputs = kwargs.pop('inputs', None)
        self._source = kwargs.pop('source', None)

        self._name = yaml['name'].split('/')[-1]
        self._description = yaml['description']

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

    def develDocs(self):
        """
        Method for adding developer links (github, doxygen, etc.) to the markdown output.
        """

        # The markdown to output
        md = []


        # Repository link(s)
        if self._config['repo']:
            items = []
            for fname in self._src:
                items.append(os.path.basename(fname))
                items.append(os.path.join(self._config['repo'], fname))
            md += ['* Source: ' + ('[{}]({}) '*len(self._src)).format(*items)]

        # Doxygen link
        if self._config['doxygen']:
            md += ['* Class Doxygen: [{0}]({1}class{0}.html)'.format(self._name, self._config['doxygen'])]
            md += ['']

        if md:
            md.insert(0, '## Additional Developer Documentation')


        return md


    def markdown(self):

        # Build a list of strings to be separated by '\n'
        md = []

        # The class title
        md += ['# {}'.format(self._name)]
        md += ['']

        # The class description
        md += [self._description]
        md += ['']

        # The details
        md += ['{{!{}!}}'.format(self._details)]
        md += ['']
        if not os.path.exists(self._details_abspath):
            self.log.error('Details file does not exist: {}'.format(self._details_abspath))

        # Print the InputParameter tables
        md += ['## Input Parameters']
        for name, table in self._tables.iteritems():
            if table.size() == 0:
                continue
            md += ['### {} Parameters'.format(name)]
            md += [table.markdown()]
            md += ['']

        # Developer links
        md += self.develDocs()

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
            for k, db in items.iteritems():
                if self._name in db:
                    md += ['### {}'.format(k)]
                    md += ['<div style="max-height:350px;overflow-y:Scroll">\n']
                    for j in db[self._name]:
                        md += [j.markdown()]
                    md += ['\n</div>']
                    md += ['']

        if md:
            md.insert(0, '## {}'.format(title))
            md += ['']

        return md
