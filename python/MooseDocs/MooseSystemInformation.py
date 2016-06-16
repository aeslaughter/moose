import logging
import os
from MooseInformationBase import MooseInformationBase
from MarkdownTable import MarkdownTable
from MooseObjectParameterTable import MooseObjectParameterTable

class MooseSystemInformation(MooseInformationBase):

    log = logging.getLogger('MkMooseDocs.MooseSystemInformation')

    def __init__(self, node, syntax, **kwargs):
        MooseInformationBase.__init__(self, node, **kwargs)
        self._syntax = syntax

    @staticmethod
    def filename(name):
        return '{}/Overview.md'.format(name.strip('/').replace('/*', '').replace('/<type>', ''))

    def markdown(self):

        md = []

        # The details
        md += ['{{!{}!}}'.format(self._details)]
        md += ['']
        if not os.path.exists(self._details):
            self.log.error('Details file does not exist: {}'.format(self._details))

        if self._yaml['parameters']:
            table = MooseObjectParameterTable()
            for param in self._yaml['parameters']:
                table.addParam(param)

            md += ['## Input Parameters']
            md += [table.markdown()]
            md += ['']


        if self._yaml['subblocks']:
            table = MarkdownTable('Name', 'Description')
            for child in self._yaml['subblocks']:

                name = child['name']
                if name.endswith('*') or name.endswith('<type>'):
                    continue

                name = name.split('/')[-1].strip()
                if self._syntax.hasObject(name):
                    name = '[{0}]({0}.md)'.format(name)
                    desc = child['description'].strip()
                    table.addRow(name, desc)

            if table.size() > 0:
                md += ['## Available Objects']
                md += [table.markdown()]
                md += ['']

        return '\n'.join(md)
