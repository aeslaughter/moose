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

    def __init__(self, yaml_data, filename, source_dirs, **kwargs):

        # Extract the input/source link directories to utilize and build databases
        inputs = collections.OrderedDict()
        source = collections.OrderedDict()
        links = kwargs.pop('links', dict())
        hide = kwargs.pop('hide', list())
        for key, value in links.iteritems():
            inputs[key] = database.Database('.i', value, database.items.InputFileItem)
            source[key] = database.Database('.h', value, database.items.ChildClassItem)

        self._filename = filename
        self._prefix = os.path.splitext(self._filename)[0]

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

        #self.writeYAML(self._filename)

        for system in self._systems:
            system.write(prefix=self._prefix)

        for obj in self._objects:
            obj.write(prefix=self._prefix)

    def writeYAML(self, filename):
        """
        Generates the System.yml file.
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


        def sub(node, level = 0):

            if hasLabel(node, local=False):

                name = node['name']
                key = name.split('/')[-1]
                subblocks = node['subblocks']


                if key == 'PolycrystalRandomIC':
                    print 'WTF', name, node['labels']


                if key == '*' or key == '<type>':
                    level -= 1

                if name in self._syntax.systems():


                    if key == '*' or key == '<type>':
                        #level -= 1
                        parent = name.split('/')[-2]
                        msg = '{}- {}:'.format(' '*4*level, parent)
                        yield msg


                        if hasLabel(node, local=True):
                            parent = name.rsplit('/', 1)[0]
                            #overview = parent.strip('/').replace('/*', '').replace('/', '-')
                            msg = '{}- Overview: {}/{}'.format(' '*4*(level+1), self._prefix, MooseSystemInformation.filename(parent))
                            yield msg
                            #level -= 1

                    else:

                        msg = '{}- {}:'.format(' '*4*level, key)
                        yield msg


                        if hasLabel(node, local=True):
                            msg = '{}- Overview: {}/{}'.format(' '*4*(level+1), self._prefix, MooseSystemInformation.filename(name))
                            yield msg




                else:
                    if subblocks == None:#key != '<type>' and key != '*':
                        #level -= 1
                        #print 'OBJECT', name
                        if hasLabel(node, local=True):

                            msg = '{0}- {1}: {2}/{1}.md'.format(' '*4*level, key, self._prefix)
                            yield msg

                    #elif key == '<type>' or key == '*':
                    #    level -= 1


                if node['subblocks'] != None:
                    for child in node['subblocks']:
                        output = sub(child, level+1)
                        for out in output:
                            yield out


        self.log.info('Creating YAML file: {}'.format(filename))
        output = []
        for node in self._yaml_data.get():
            output += sub(node)

        fid = open(filename, 'w')
        fid.write('\n'.join(output))
        fid.close()
