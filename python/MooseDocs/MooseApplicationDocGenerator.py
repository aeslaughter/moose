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
        source_dirs[list]: The source directories to inspect and build documentation.

    Kwargs:
        input[list] A list of directories to search for input files containing the class name in an input file.
        source[list] A database linking the class name to use in source.
    """

    log = logging.getLogger('MkMooseDocs.MooseApplicationDocGenerator')

    def __init__(self, yaml_data, prefix, source_dirs, **kwargs):

        # Extract the input/source link directories to utilize and build databases
        inputs = collections.OrderedDict()
        source = collections.OrderedDict()
        links = kwargs.pop('links', dict())
        hide = kwargs.pop('hide', list())
        for key, value in links.iteritems():
            inputs[key] = database.Database('.i', value, database.items.InputFileItem)
            source[key] = database.Database('.h', value, database.items.ChildClassItem)

        self._prefix = prefix

        # Read the supplied files
        self._yaml_data = yaml_data
        self._syntax = MooseApplicationSyntax(yaml_data, self._prefix, *source_dirs)


        self._systems = []
        for system in self._syntax.systems():
            md = self._syntax.getMarkdown(system)
            node = yaml_data.find(system)
            if node['name'] not in hide:
                self._systems.append(MooseSystemInformation(node, md))

        self._objects = []
        for key, value in self._syntax.objects().iteritems():
            md = self._syntax.getMarkdown(key)
            header = self._syntax.header(key)
            nodes = yaml_data[key]
            for node in nodes:
                if not any([node['name'].startswith(h) for h in hide]):
                    self._objects.append(MooseObjectInformation(node, md, header, inputs=inputs, source=source))

    def write(self):

        self.writeYAML()

        #for system in self._systems:
        #    system.write(prefix=self._prefix)

        #for obj in self._objects:
        #    obj.write(prefix=self._prefix)

    def writeYAML(self):
        """
        Generates the System.yml file.
        """


        """
        def hasLabel(node, **kwargs):

            label = self._prefix
            local = kwargs.pop('local', False)

            if ('labels') in node and (label in node['labels']):
                return True

            if not local and node['subblocks'] != None:
                out = []
                for child in node['subblocks']:
                    out.append(hasLabel(child))
                return any(out)

            return False
        """

        #def insertItem(tree, cmd, item):
        #    cmd = "tree{}'.format(("['{}']"*level).format(*relative))



        rec_dd = lambda: collections.defaultdict(rec_dd)
        tree = rec_dd()
        for root, dirs, files in os.walk(self._prefix, topdown=True):

            if 'Overview.md' in files:
                files.insert(0, files.pop(files.index('Overview.md')))

            for filename in files:
                name, ext = os.path.splitext(filename)

                if ext != '.md':
                    continue

                relative = root.replace(self._prefix, '').strip('/').split('/')
                level = len(relative)

                #print '{}- {}:{}'.format(' '*4*level, name, filename)

                #cmd = "tree{}'{}'".format(("['{}']"*level).format(*relative), filename)
                #insertItem(tree, relative, filename)

                #cmd = "tree{}['items'].append('{}')".format(("['{}']"*level).format(*relative), filename)
                cmd = "tree{}".format(("['{}']"*level).format(*relative))

                #print cmd
                d = eval(cmd)
                if 'items' not in d:
                    d['items'] = []

                d['items'].append( (name, os.path.join(root, filename)))


        def output(node, level=0):



            keys = node.keys()
            print keys

            for k in keys:
                v = node[k]
                if k == 'items':
                    for item in v:
                        print '{}- {}: {}'.format(' '*4*(level), *item)
                else:
                    print '{}- {}:'.format(' '*4*level, k)
                    output(v, level+1)

        output(tree)

        """
        self.log.info('Creating YAML file: {}'.format(filename))
        output = []
        for node in self._yaml_data.get():
            output += sub(node)

        fid = open(filename, 'w')
        fid.write('\n'.join(output))
        fid.close()
        """
