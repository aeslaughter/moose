import os
import re

class MooseApplicationSyntax(object):
    """
    An object for handling the registered object and action syntax for a specific directory.


    A compiled MOOSE application contains all included libraries (i.e., framework, modules, and other applications), thus
    when an application is executed with --yaml in includes the complete syntax.

    To allow for documentation to be generated to only include the objects and syntax specific to an application the syntax
    defined in the application source directory must be separated from that of the entire library. This object builds maps to
    the registered objects and syntax specific to the application.

    Args:
        yaml[MooseYaml]: The MooseYaml object obtained by running the application with --yaml option.
        args: Valid source directory(ies) to extract syntax from.
    """

    def __init__(self, yaml, *args):

        # The supplied variables
        self._yaml = yaml
        self._path = path

        # The databases containing the system/object/markdown/source information for this directory
        self._moosebase = dict()
        self._syntax = set()
        self._register = dict()
        self._filenames = dict()
        self._markdown = dict()

        # Update the 'moosebase' database
        for itr in self._yaml.get():
            _getdata(itr)

        # Update the syntax maps
        for path in args:
            self._updateSyntax(path)

    def syntax(self):
        """
        Return the syntax defined in the supplied applications.
        """
        return self._syntax


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
                getdata(child)

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
                        self._register[key] = key

                    # Map of named registered objects
                    for match in re.finditer(r'registerNamed\w+?\((?P<class>\w+),\s*"(?P<key>\w+)"\);', content):
                        self._register[match.group('class')] = match.group('key')

                    # Action syntax map
                    for match in re.finditer(r'registerActionSyntax\("(?P<action>\w+)"\s*,\s*"(?P<syntax>.*?)\"[,\);]', content):
                        self._syntax.add(match.group('syntax'))
