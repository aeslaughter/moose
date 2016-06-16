import os
import logging
import collections

from MooseSystemInformation import MooseSystemInformation
from MooseObjectInformation import MooseObjectInformation
from MooseApplicationSyntax import MooseApplicationSyntax
import database

class MooseApplicationDocGenerator(object):
    """
    Generate documentation for an application, for a given directory.

    Args:
        yaml_data[dict]: The complete YAML object obtained from the MOOSE application.
        filename[str]: The MkDocs yaml file to create.
        config[dict]: A dictionary with configuration options.
            repo:
            prefix:
            details:
            source:

    Kwargs:
        input[list] A list of directories to search for input files containing the class name in an input file.
        source[list] A database linking the class name to use in source.
    """

    log = logging.getLogger('MkMooseDocs.MooseApplicationDocGenerator')

    def __init__(self, yaml_data, config, **kwargs):

        # Extract the input/source link directories to utilize and build databases
        links = kwargs.pop('links', dict())
        hide = kwargs.pop('hide', list())

        # Configuration
        self._config = config

        # Create the database of input files and source code
        inputs = collections.OrderedDict()
        source = collections.OrderedDict()
        for key, value in links.iteritems():
            inputs[key] = database.Database('.i', value, database.items.InputFileItem)
            source[key] = database.Database('.h', value, database.items.ChildClassItem)

        # Read the supplied files
        self._yaml_data = yaml_data
        self._syntax = MooseApplicationSyntax(yaml_data, self._config.get('source_dir'))

        self._systems = []
        for system in self._syntax.systems():
            node = yaml_data.find(system)
            if node['name'] not in hide:
                self._systems.append(MooseSystemInformation(node, self._syntax, **self._config))

        self._objects = []
        for key, value in self._syntax.objects().iteritems():
            src = self._syntax.filenames(key)
            nodes = yaml_data[key]
            for node in nodes:
                if not any([node['name'].startswith(h) for h in hide]):
                    self._objects.append(MooseObjectInformation(node, src, inputs=inputs, source=source, **self._config))

    def write(self):

        print self._systems
        for system in self._systems:
            system.write()

        for obj in self._objects:
            obj.write()

        yml = self.generateYAML()


        filename = os.path.abspath(os.path.join(self._config.get('build_dir'), self._config['source_dir'], 'pages.yml'))


        """

        if os.path.exists(filename):
            with open(filename, 'r') as fid:
                content = fid.read()
            if content == yml:
                return
        """

        self.log.info('Creating YAML file: {}'.format(filename))
        with open(filename, 'w') as fid:
            fid.write(yml)


    def generateYAML(self):
        """
        Generates the System.yml file.
        """

        prefix = os.path.join(self._config.get('build_dir'), self._config['source_dir'])

        rec_dd = lambda: collections.defaultdict(rec_dd)
        tree = rec_dd()
        for root, dirs, files in os.walk(prefix, topdown=True):

            if 'Overview.md' in files:
                files.insert(0, files.pop(files.index('Overview.md')))

            for filename in files:
                name, ext = os.path.splitext(filename)

                if ext != '.md':
                    continue

                relative = root.lstrip(self._config['docs_dir']).lstrip(prefix).strip('/').split('/')
                level = len(relative)
                cmd = "tree{}".format(("['{}']"*level).format(*relative))

                d = eval(cmd)
                if 'items' not in d:
                    d['items'] = []

                d['items'].append( (name, os.path.join(os.path.relpath(root, self._config['docs_dir']), filename)))


        def dumptree(node, level=0):

            if 'items' in node:
                for item in node['items']:
                    yield '{}- {}: {}'.format(' '*4*(level), *item)
                node.pop('items')

            for key, value in node.iteritems():
                yield '{}- {}:'.format(' '*4*level, key)
                for f in dumptree(value, level+1):
                    yield f

        output = dumptree(tree)
        return '\n'.join(output)
