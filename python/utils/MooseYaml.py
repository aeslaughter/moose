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
        raw = raw.split('**START YAML DATA**\n')[1]
        raw = raw.split('**END YAML DATA**')[0]
        self._data = yaml.load(raw, Loader=Loader)

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

    def __iter__(self):
        """
        Make this class iterable over the complete YAML data structure.
        """
        pass

    def dump(self):
        for itr in self._data:
            self._printName(itr)

    @staticmethod
    def _printName(data, level=0):

        print ' '*2*level, os.path.basename(data['name'])

        if data['subblocks']:
            for child in data['subblocks']:
                MooseYaml._printName(child, level+1)

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
