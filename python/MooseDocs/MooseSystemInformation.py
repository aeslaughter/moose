import logging
import os
from MooseInformationBase import MooseInformationBase
from MarkdownTable import MarkdownTable
from MooseObjectParameterTable import MooseObjectParameterTable

class MooseSystemInformation(MooseInformationBase):

    log = logging.getLogger('MkMooseDocs.MooseSystemInformation')

    def __init__(self, node, details):
        MooseInformationBase.__init__(self, node)

        self._details = details


    def markdown(self):

        md = []

        # The details
        if self._details and os.path.exists(self._details):
            md += ['{{!{}!}}'.format(self._details)]
        else:
            md += ['<p style="color:red;font-size:120%">']
            md += ['ERROR: Failed to located system detailed description: {}'.format(self._yaml['name'])]
            md += ['</p>']
            self.log.error('Failed to load system description: {}'.format(self._yaml['name']))

        if self._yaml['parameters']:
            table = MooseObjectParameterTable()
            for param in self._yaml['parameters']:
                table.addParam(param)

            md += ['## Input Parameters']
            md += [table.markdown()]


        if self._yaml['subblocks']:
            table = MarkdownTable('Name', 'Description')
            for child in self._yaml['subblocks']:
                name = child['name']
                desc = child['description']

                if name.endswith('*'):
                    continue

                table.addRow(name.split('/')[-1], desc)

            md += ['## Available Objects']
            md += [table.markdown()]

        return '\n'.join(md)
