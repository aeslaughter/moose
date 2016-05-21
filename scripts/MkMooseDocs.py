#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import MooseDocs
import errno

#TODO: Make this a generic function in /moose/python/utils
from peacock.utils.ExeLauncher import runExe


def find_moose_executable(loc, **kwargs):
    """

    Args:
        loc[str]: The directory containing the MOOSE executable.

    Kwargs:
        methods[list]: (Default: ['opt', 'oprof', 'dbg']) The list of build types to consider.
        name[str]: (Default: opt.path.basename(loc)) The name of the executable to locate.
    """

    # Set the methods and name local varaiables
    methods = kwargs.pop('methods', ['opt', 'oprof', 'dbg'])
    name = kwargs.pop('name', os.path.basename(loc))

    # Check that the location exists and that it is a directory
    if not os.path.isdir(loc):
        print 'ERROR: The supplied path must be a valid directory:', loc
        return errno.ENOTDIR

    # Search for executable with the given name
    exe = errno.ENOENT
    for method in methods:
        exe = os.path.join(loc, name + '-' + method)
        if os.path.isfile(exe):
            break

    # Returns the executable or error code
    if not errno.ENOENT:
        print 'ERROR: Unable to locate a valid MOOSE executable in directory'
    return exe



class Database(object):
    def __init__(self, ext, path):
        self._database = dict()


        for root, dirs, files in os.walk(path, topdown=False):
            for filename in files:
                if filename.endswith(ext):
                    self.update(os.path.join(root, filename))

    def update(self, filename):
        pass


    def __getitem__(self, key):
        return self._database[key]


    def markdown(self, key):
        return []

    @staticmethod
    def content(filename):
        fid = open(filename, 'r')
        content = fid.read()
        fid.close()
        return content


class MooseObjectMarkdownDatabase(Database):
    def __init__(self, path):
        Database.__init__(self, '.md', path)

    def update(self, filename):

        name = os.path.basename(filename)[0:-3]

        self._database[name] = '{{!{}!}}'.format(filename)

    def markdown(self, key):
        return self._database[key]


class RegexDatabase(Database):
    def __init__(self, ext, regex, path):
        self._regex = regex
        Database.__init__(self, ext, path)



    def update(self, filename):
        content = self.content(filename)

        for match in re.finditer(self._regex, content):
            grp1 = match.group(1)
            if grp1 not in self._database:
                self._database[grp1] = []

            rel = filename.split('/moose/')[-1]
            repo = MooseDocs.MOOSE_REPOSITORY + rel

            self._database[grp1].append( (rel, repo) )

    def markdown(self, key):
        input = self[key]

        md = []
        for rel, repo in input:
            md += ['* [{}]({})'.format(rel, repo)]
        return '\n'.join(md)




class InputFileDatabase(RegexDatabase):
    def __init__(self, path):
        RegexDatabase.__init__(self, '.i', r'type\s*=\s*(\w+)\b', path)

class ChildClassDatabase(RegexDatabase):
    def __init__(self, path):
        RegexDatabase.__init__(self, '.h', r'public\s*(\w+)\b', path)


class MooseObjectInformation(object):
    """


    """



    def __init__(self, yaml, databases, **kwargs):

        prefix = kwargs.pop('prefix', '')

        self._databases = databases

        # Extract basic name and description from yaml data
        self._class_path = os.path.join(MooseDocs.MOOSE_DOCS_DIR, prefix) + str(yaml['name'])

        self._class_name = yaml['name'].split('/')[-1]
        self._class_description = yaml['description']

        # Read the markdown details markdown file
        #fid = open(str(details))
        #self._class_detail = fid.read()
        #fid.close()

        self._tables = collections.OrderedDict()
        for param in yaml['parameters']:
            name = param['group_name']
            if not name and param['required']:
                name = 'Required'
            elif not name and not param['required']:
                name = 'Optional'

            if name not in self._tables:
                self._tables[name] = MooseDocs.parsing.MooseObjectParameterTable()

            self._tables[name].addParam(param)

    def __str__(self):
        return self.markdown()

    def write(self):

        dir_name = os.path.dirname(self._class_path)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        fid = open(self._class_path + '.md', 'w')
        fid.write(self.markdown())
        fid.close()

    def markdown(self):

        # Build a list of strings to be separated by '\n'
        md = []

        # The class title
        md += ['# {}'.format(self._class_name)]
        md += ['']

        # The class description
        md += ['## Class Description']
        md += [self._class_description]
        md += ['']

        # The details
        details = self._databases.pop('details')
        md += [details.markdown(self._class_name)]
        md += ['']

        # Re-order the table to insert 'Required' and 'Optional' first
        tables = collections.OrderedDict()
        keys = ['Required', 'Optional']
        for k in keys:
            if k in self._tables:
                tables[k] = self._tables.pop(k)
        for k, t in self._tables.iteritems():
            tables[k] = t

        # Print the InputParameter tables
        md += ['## Input Parameters']
        for name, table in tables.iteritems():
            md += ['### {} Parameters'.format(name)]
            md += [table.markdown()]
            md += ['']

        # Print the input file use
        md += ['## Input File Usage']
        for key, db in self._databases.iteritems():
            md += ['### {}'.format(key)]
            md += [db.markdown(self._class_name)]
            md += ['']

        return '\n'.join(md)



if __name__ == '__main__':

    #TODO: Add 'moose_base' to yaml
    db = dict()

    db['details'] = MooseObjectMarkdownDatabase(os.path.join(MooseDocs.MOOSE_DIR, 'framework', 'include'))
   # print db['Diffusion']

    db['Tutorials'] = InputFileDatabase(os.path.join(MooseDocs.MOOSE_DIR, 'tutorials'))
    db['Tests'] = InputFileDatabase(os.path.join(MooseDocs.MOOSE_DIR, 'test', 'tests'))

    db['Examples'] = InputFileDatabase(os.path.join(MooseDocs.MOOSE_DIR, 'examples'))


    db['Examples'] = ChildClassDatabase(os.path.join(MooseDocs.MOOSE_DIR, 'examples'))

   # children = db.markdown('Diffusion')
    #print children

    # Locate the MOOSE executable
    exe = find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'test'), name='moose_test')
    #if isinstance(exe, int):
    #    print os.strerror(exe)

    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)


    path = '/Kernels/Diffusion'
    info = MooseObjectInformation(ydata[path], db, prefix='framework')
    info.write()
