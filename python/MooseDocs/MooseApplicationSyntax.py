import os
import re
import collections
import logging
import MooseDocs

class MooseApplicationSyntax(object):
    """
    An object for handling the registered object and action syntax for a specific set of directories.

    A compiled MOOSE application contains all included libraries (i.e., framework, modules, and other applications), thus
    when an application is executed with --yaml in includes the complete syntax.

    To allow for documentation to be generated to only include the objects and syntax specific to an application the syntax
    defined in the application source directory must be separated from that of the entire library. This object builds maps to
    the registered objects and syntax specific to the application.

    Args:
        yaml[MooseYaml]: The MooseYaml object obtained by running the application with --yaml option.
        args: Valid source directory(ies) to extract syntax from.
    """

    def __init__(self, yaml_data, *args):

        self._log = logging.getLogger(self.__class__.__name__)
        self._handler = logging.StreamHandler()
        self._log.setLevel(logging.ERROR)
        self._log.addHandler(self._handler)


        # The databases containing the system/object/markdown/source information for this directory
        self._moosebase = dict()
        self._actions = list()
        self._objects = dict()
        self._filenames = dict()
        self._markdown = dict()
        self._syntax = collections.OrderedDict()

        # Update the 'moosebase' database
        for itr in yaml_data.get():
            self._getdata(itr)

        # Update the syntax maps
        for path in args:
            self._updateSyntax(path)

        # Create the syntax tree local the supplied directories
        self._buildLocalSyntaxTree()

    def syntax(self):
        """
        Return the application syntax map.
        """
        return self._syntax

    def systems(self):
        """
        Return a set of MOOSE systems for defined in the supplied directories.
        """

        output = set()
        for action in self._actions:
            output.add(action.replace('/*', '').split('/')[-1])
            ###output.add( (action, action.replace('/*', '').split('/')[-1]) )
        return output


    def hasSyntax(self, key):
        """
        Return True if the supplied key is registered syntax of the supplied directories.

        Args:
            key[str]: The name of the system to check.
        """

        return (key in self._actions) or (key + '/*' in self._actions)


    def getMarkdown(self, name):

        if name in self._markdown:
            return self._markdown[name]

        self._log.error('Failed to locate the system documentation for {}'.format(name))
        return None
        #return os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'FileNotFound.md')

    def _getdata(self, data):
        """
        A helper for populating the 'moosebase' database. (private)

        Args:
            data: The YAML node to examine.
        """
        if 'moosebase' in data:
            m = data['moosebase']
            if m not in self._moosebase:
                self._moosebase[m] = []
            self._moosebase[m].append(data['name'])

        if data['subblocks']:
            for child in data['subblocks']:
                self._getdata(child)

    def _updateSyntax(self, path):
        """
        A helper for populating the syntax/filename/markdown databases. (private)

        Args:
            path[str]: A valid source directory to inspect.
        """

        # Walk the directory, looking for files with the supplied extension.
        for root, dirs, files in os.walk(path, topdown=False):
            for filename in files:
                fullfile = os.path.join(root, filename)

                # Store any markdown files associated (the name of the markdown matches should match the registered name).
                if filename.endswith('.md'):
                    self._markdown[filename[:-2]] = fullfile

                # Inspect source files
                if filename.endswith('.C') or filename.endswith('.h'):

                    fid = open(fullfile, 'r')
                    content = fid.read()
                    fid.close()

                    # Update class to source definition map
                    if filename.endswith('.h'):
                        for match in re.finditer(r'class\s*(?P<class>\w+)', content):
                            self._filenames[match.group('class')] = fullfile

                    # Map of registered objects
                    for match in re.finditer(r'register\w+?\((?P<key>\w+)\);', content):
                        key = match.group('key')
                        self._objects[key] = key

                    # Map of named registered objects
                    for match in re.finditer(r'registerNamed\w+?\((?P<class>\w+),\s*"(?P<key>\w+)"\);', content):
                        self._objects[match.group('class')] = match.group('key')

                    # Action syntax map
                    for match in re.finditer(r'registerActionSyntax\("(?P<action>\w+)"\s*,\s*"(?P<syntax>.*?)\"[,\);]', content):
                        self._actions.append(match.group('syntax'))

            yml = dict()

    def _buildLocalSyntaxTree(self):
        """
        A helper for creating the syntax tree for the supplied source directories for this application.
        """

        def attach(branch, key, trunk):
            """
            Insert a branch of directories on its trunk.
            """
            parts = branch.split('/', 1)
            key = parts[0]

            if key not in trunk:
                trunk[key] = collections.OrderedDict()
                trunk[key]['key'] = '{}/{}'.format(trunk['key'], key)

            if len(parts) == 2:
                node, others = parts
                attach(others, key, trunk[key])

        for syntax in self._actions:
            key = syntax.split('/')[0]
            if key not in self._syntax:
                self._syntax[key] = collections.OrderedDict()
                self._syntax[key]['key'] = '/{}'.format(key)
            attach(syntax, key, self._syntax)
