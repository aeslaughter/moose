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


    def __getitem__(self, key):
        """
        Operator [] access to the yaml blocks.

        Args:
            key[str]: The yaml key to return.
        """
        for itr in self._data:
            result = self._search(key, itr)
            if result:
                return result

    @staticmethod
    def _search(key, data):
        """
        A helper method for locating the desired yaml data.
        """
        if data['name'].endswith(key):
            return data

        if not data['subblocks']:
            return None

        for child in data['subblocks']:
            child_data = MooseYaml._search(key, child)
            if child_data:
                return child_data
        return None

    @staticmethod
    def _print(data, level=0):

        output = []
        output.append(' '*2*level + data['name'])

        if data['subblocks']:
            for child in data['subblocks']:
                output += MooseYaml._print(child, level+1)

        return output
