import os
import yaml
from yaml import CLoader as Loader, CDumper as Dumper


class MooseYaml(object):
    """
    A utility to read the YAML data from MOOSE.

    Args:
        raw[str]: The raw yaml output from MOOSE.
    """
    def __init__(self, raw):
        raw = raw.split('**START YAML DATA**\n')[-1]
        raw = raw.split('**END YAML DATA**')[0]
        self._data = yaml.load(raw, Loader=Loader)


    def get(self):
        return self._data

    def __str__(self):

        output = []
        for itr in self._data:
            output += self._print(itr)
        return '\n'.join(output)

    def dump(self, **kwargs):
        label = kwargs.pop('label', None)
        output = []
        for itr in self._data:
            output += self._print(itr, 0, label)
        print '\n'.join(output)


    def __getitem__(self, key):
        """
        Operator [] access to the yaml blocks.

        Args:
            key[str]: The yaml key to return.
        """
        output = []
        for itr in self._data:
            output += self._search(key, itr)
        return output

    def addLabel(self, label, keys):

        for key in keys:
            for node in self[key]:
                if 'labels' not in node:
                    node['labels'] = set()
                node['labels'].add(label)

        def sub(data):
            active = set()

            if ('labels' in data) and (label in data['labels']):
                active.add(label)

            if isinstance(data, dict) and data['subblocks']:
                child_active = set()
                for child in data['subblocks']:
                    child_active.update(sub(child))

                active.update(child_active)
                if 'labels' not in data:
                    data['labels'] = set()
                data['labels'].update(active)

            return active


        for itr in self._data:
            itr['labels'] = sub(itr)


    @staticmethod
    def _search(key, data):
        """
        A helper method for locating the desired yaml data.
        """

        output = []
        if data['name'].endswith(key):
            output.append(data)

        if data['subblocks']:
            for child in data['subblocks']:
                child_data = MooseYaml._search(key, child)
                if child_data:
                    output += child_data
        return output

    @staticmethod
    def _print(data, level=0, label=None):
        output = []
        if ('labels' in data) and (label in data['labels']):
            output.append(' '*2*level + data['name'])

        if data['subblocks']:
            for child in data['subblocks']:
                output += MooseYaml._print(child, level+1, label)

        return output
