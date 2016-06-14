#!/usr/bin/env python
import os
import re
import collections
import utils #/moose/python/utils
import yaml
import logging

from mkdocs.utils import yaml_load

import subprocess

import MooseDocs

class MkMooseDocsFilter(logging.Formatter):

    COLOR = {'DEBUG':'GREEN', 'INFO':'RESET', 'WARNING':'YELLOW', 'ERROR':'RED', 'CRITICAL':'MAGENTA'}

    def format(self, record):
        msg = logging.Formatter.format(self, record)

        indent = record.name.count('.')

        if record.levelname in ['WARNING', 'ERROR', 'CRITICAL']:
            msg = '{}{}: {}'.format(' '*4*indent, record.levelname, msg)
        else:
            msg = '{}{}'.format(' '*4*indent, msg)

        if record.levelname in self.COLOR:
            msg = utils.colorText(msg, self.COLOR[record.levelname])

        return msg

#TODO: Make this a generic function in /moose/python/utils
#from peacock.utils.ExeLauncher import runExe
def runExe(app_path, args):

    popen_args = [str(app_path)]
    if isinstance(args, str):
        popen_args.append(args)
    else:
        popen_args.extend(args)

    proc = subprocess.Popen(popen_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = proc.communicate()
    stdout_data = data[0].decode("utf-8")
    return stdout_data



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
            inputs[key] = MooseDocs.database.Database('.i', value, MooseDocs.database.items.InputFileItem)
            source[key] = MooseDocs.database.Database('.h', value, MooseDocs.database.items.ChildClassItem)

        self._filename = filename
        self._prefix = os.path.splitext(self._filename)[0]

        # Read the supplied files
        self._yaml_data = yaml_data
        self._syntax = MooseDocs.MooseApplicationSyntax(yaml_data, self._prefix, *source_dirs, hide=hide)

        """
        self._systems = []
        for system in self._syntax.systems():
            md = self._syntax.getMarkdown(system)
            self._systems.append(MooseDocs.MooseSystemInformation(yaml_data[system], md))

        self._objects = []
        for key, value in self._syntax.objects().iteritems():
            md = self._syntax.getMarkdown(key)
            header = self._syntax.header(key)
            node = yaml_data[key]
            if node:
                self._objects.append(MooseDocs.MooseObjectInformation(node, md, header, inputs=inputs, source=source))
        """

    def write(self):

        self.buildYaml(self._filename)

#        prefix = os.path.splitext(self._filename)[0]os.path.splitext(self._filename)[0]

        #for system in self._systems:
        #    system.write(prefix=prefix)

        #for obj in self._objects:
        #  obj.write(prefix=prefix)

    def buildYaml(self, filename):
        """
        Generates the System.yml file.
        """

        def hasSubBlock(name, node):
            if node['subblocks'] != None:
                for sub in node['subblocks']:
                    if name == sub['name']:# and ('labels' in sub) and (self._prefix in sub['labels']):
                        return True
            return False

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



        #print self._yaml_data
        #self._yaml_data.dump(label=self._prefix)


        def sub(node, level = 0):

            if hasLabel(node, local=False):

                name = node['name']
                key = name.split('/')[-1]
                #star = '{}/*'.format(name)
                subblocks = node['subblocks']

                if key == '<type>':
                    level -= 1

                elif key == '*':
                    if hasLabel(node, local=True):
                        parent = name.rsplit('/', 1)[0]
                        overview = parent.strip('/').replace('/', '-')
                        msg = '{}- Overview: {}.md'.format(' '*4*level, overview)
                        yield msg

                elif subblocks != None:

                    msg = '{}- {}:'.format(' '*4*level, key)
                    yield msg

                    if hasLabel(node, local=True):
                        overview = name.strip('/').replace('/', '-')
                        msg = '{}- Overview: {}.md'.format(' '*4*(level+1), overview)
                        yield msg

                else:
                    msg = '{0}- {1}: {1}.md'.format(' '*4*level, key)
                    yield msg


                if node['subblocks'] != None:
                    for child in node['subblocks']:
                        output = sub(child, level+1)
                        for out in output:
                            yield out
                        #if name in syntax._objects:
                        #    msg = '{0}- {1}: {1}.md'.format(' '*4*(level+1), name)
                        #    self.log.debug(msg)
                        #    yield msg



            #if node['subblocks'] != None:
            #    for child in node['subblocks']:
            #        output.append(sub(child))
            #return output

        """
        def sub(syntax, key, node, level=0):

            #TODO: Convert this to use pyyaml

            ynode = self._yaml_data[node['key']]


        """

        self.log.info('Creating YAML file: {}'.format(filename))
        output = []
        for node in self._yaml_data.get():
            output += sub(node)

        fid = open(filename, 'w')
        fid.write('\n'.join(output))
        fid.close()


if __name__ == '__main__':

    # Some arguments to be passed in
    dirname = os.path.join(MooseDocs.MOOSE_DIR, 'docs')

    # Setup the logger object
    log = logging.getLogger('MkMooseDocs')
    handler = logging.StreamHandler()
    formatter = MkMooseDocsFilter()#'%(name)s:%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    #log.setLevel(logging.DEBUG)

    # Setup the location
    config_file = os.path.join(dirname, 'mkdocs.yml')
    log.info('Generating Documentation: {}'.format(config_file))

    # Parse the configuration file for the desired paths
    os.chdir(dirname)
    fid = open(config_file, 'r')
    config = yaml_load(fid.read())
    fid.close()


    # Locate and run the MOOSE executable
    exe = utils.find_moose_executable(os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'phase_field'), name='phase_field')
    raw = runExe(exe, '--yaml')
    ydata = utils.MooseYaml(raw)

    #nodes = ydata['/Kernels/*']
    #for node in nodes:
    #        print node['name'], node.keys()

    #nodes = ydata['ClosePackIC']
    #for node in nodes:
    #    print node['name']

    #ydata.pop('/UserObjects/PointValue')
    #print ydata['/UserObjects/PointValue']

    #path = config['extra']['Generate']['Phase Field']['source']
    #syntax = MooseDocs.MooseApplicationSyntax(ydata, 'phase_field', *path)
    #print syntax._yaml_data


    for value in config['extra']['generate'].values():
        generator = MooseApplicationDocGenerator(ydata, value['yaml'], value['source'], links=config['extra']['links'], hide=config['extra']['hide'])
        generator.write()

    #print '\n'.join(generator._syntax._syntax)

    """
    node = ydata['/Kernels']
    info = MooseDocs.MooseSystemInformation(node)
    info.write()
    """

    """
    path = '/Kernels/Diffusion'
    details = '/Users/slauae/projects/moose-doc/framework/include/kernels/Diffusion.md'
    source = '/Users/slauae/projects/moose-doc/framework/include/kernels/Diffusion.h'
    info = MooseDocs.MooseObjectInformation(ydata[path], details, source, inputs=inputs, source=source)
    info.write()
    """
