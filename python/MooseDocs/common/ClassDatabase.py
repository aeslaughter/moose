"""Tools for extracting C++ class information."""
import os
import re
import multiprocessing

import mooseutils

import MooseDocs


class DatabaseItem(object):
    def __init__(self, name, header, source):
        self.name = name
        self.source = source
        self.header = header
        self.inputs = set()
        self.children = set()

    def __str__(self):
        return '{} {}'.format(self.name, self.inputs)

class ClassDatabase(object):
    DEFINITION_RE = re.compile(r'class\s*(?P<class>\w+)\b[^;]')
    CHILD_RE = re.compile(r'\bpublic\s+(?P<key>\w+)\b')
    INPUT_RE = re.compile(r'\btype\s*=\s*(?P<key>\w+)\b')

    def __init__(self, include_dirs, input_dirs):

        self.__objects = dict()

        headers = self.__locateFilenames(include_dirs, '.h')
        inputs = self.__locateFilenames(include_dirs, '.i')

       # print '\n'.join(headers)

        self.__process(headers, ClassDatabase.DEFINITION_RE, self.__matchDefinition)
        self.__process(headers, ClassDatabase.CHILD_RE, self.__matchChild)
        self.__process(inputs, ClassDatabase.INPUT_RE, self.__matchInput)



    def __getitem__(self, key):
        return self.__objects[key]

    def __contains__(self, key):
        return key in self.__objects


    @staticmethod
    def __locateFilenames(directories, ext):

        out = set()
        for location in directories:
            for base, _, files in os.walk(location):
                for fname in files:
                    full_file = os.path.join(base, fname)
                    if fname.endswith(ext) and not os.path.islink(full_file):
                        out.add(full_file)
        return out

    @staticmethod
    def __process(filenames, regex, func):
        for filename in filenames:
            with open(filename, 'r') as fid:
                content = fid.read()

            for match in regex.finditer(content):
                func(filename, match)

    def __matchDefinition(self, filename, match):

        name = match.group('class')
        src = filename.replace('/include/', '/src/')[:-2] + '.C'
        if not os.path.exists(src):
            src = None

        self.__objects[name] = DatabaseItem(name, filename, src)

    def __matchChild(self, filename, match):
        key = match.group('key')
        if key in self:
            self.__objects[key].children.add(filename)

    def __matchInput(self, filename, match):
        key = match.group('key')
        if key in self:
            self.__objects[key].inputs.add(filename)



if __name__ == '__main__':


    includes = [os.path.join(MooseDocs.ROOT_DIR)]
    inputs = [os.path.join(MooseDocs.ROOT_DIR)]

    db = ClassDatabase(includes, inputs)


    print db['Diffusion']
