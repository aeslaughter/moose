"""Tools for extracting C++ class information."""
import os
import re
import multiprocessing

import mooseutils

import MooseDocs
from eval_path import eval_path

DEFINITION_RE = re.compile(r'class\s*(?P<class>\w+)\b[^;]')
CHILD_RE = re.compile(r'\bpublic\s+(?P<key>\w+)\b')
INPUT_RE = re.compile(r'\btype\s*=\s*(?P<key>\w+)\b')

class DatabaseItem(object):
    def __init__(self, name, header, source):
        self.name = name
        self.source = source
        self.header = header
        self.inputs = set()
        self.children = set()

def build_class_database(include_dirs, input_dirs):

    if isinstance(include_dirs, str):
        include_dirs = [eval_path(x) for x in include_dirs.split()]
    if isinstance(input_dirs, str):
        input_dirs = [eval_path(x) for x in input_dirs.split()]

    headers = _locateFilenames(include_dirs, '.h')
    inputs = _locateFilenames(input_dirs, '.i')

    objects = dict()
    _process(objects, headers, DEFINITION_RE, _matchDefinition)
    _process(objects, headers, CHILD_RE, _matchChild)
    _process(objects, inputs, INPUT_RE, _matchInput)
    return objects

def _locateFilenames(directories, ext):

    out = set()
    for location in directories:
        for base, _, files in os.walk(location):
            for fname in files:
                full_file = os.path.join(base, fname)
                if fname.endswith(ext) and not os.path.islink(full_file):
                    out.add(full_file)
    return out

def _process(objects, filenames, regex, func):
    for filename in filenames:
        with open(filename, 'r') as fid:
            content = fid.read()

        for match in regex.finditer(content):
            func(objects, filename, match)

def _matchDefinition(objects, filename, match):

    name = match.group('class')
    src = filename.replace('/include/', '/src/')[:-2] + '.C'
    if not os.path.exists(src):
        src = None
    else:
        src = os.path.relpath(src, MooseDocs.ROOT_DIR)

    hdr = os.path.relpath(filename, MooseDocs.ROOT_DIR)
    objects[name] = DatabaseItem(name, hdr, src)

def _matchChild(objects, filename, match):
    key = match.group('key')
    if key in objects:
        filename = os.path.relpath(filename, MooseDocs.ROOT_DIR)
        objects[key].children.add(filename)

def _matchInput(objects, filename, match):
    key = match.group('key')
    if key in objects:
        filename = os.path.relpath(filename, MooseDocs.ROOT_DIR)
        objects[key].inputs.add(filename)

if __name__ == '__main__':
    includes = [os.path.join(MooseDocs.ROOT_DIR)]
    inputs = [os.path.join(MooseDocs.ROOT_DIR)]
    db = build_class_database(includes, inputs)
    print db['Diffusion'].source
    print db['Diffusion'].header
    print db['Diffusion'].children
    print db['Diffusion'].inputs
