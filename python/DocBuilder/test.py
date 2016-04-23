#!/usr/bin/env python
import os
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print 'SLOW'
    from yaml import Loader, Dumper
from peacock.utils.ExeLauncher import runExe




class YamlData(object):
    def __init__(self, raw):
        raw = raw.split('**START YAML DATA**\n')[1]
        raw = raw.split('**END YAML DATA**')[0]
        self._data = yaml.load(raw, Loader=Loader)

    def __getitem__(self, key):
        for iter in self._data:
            result = self._search(key, iter)
            if result:
                return result

    @staticmethod
    def _search(key, data):
        if data['name'].endswith(key):
            return data

        if not data['subblocks']:
            return None

        for child in data['subblocks']:
            child_data = YamlData._search(key, child)
            if child_data:
                return child_data
        return None



if __name__ == '__main__':

    app = os.path.join(os.environ['MOOSE_DIR'], 'test', 'moose_test-oprof')
    args = '--yaml'
    raw = runExe(app, args)

    ydata = YamlData(raw)

    diff = ydata['/Kernels/Diffusion']

    print yaml.dump(diff)
