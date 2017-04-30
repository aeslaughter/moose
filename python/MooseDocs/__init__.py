#pylint: disable=missing-docstring
#################################################################
#                   DO NOT MODIFY THIS HEADER                   #
#  MOOSE - Multiphysics Object Oriented Simulation Environment  #
#                                                               #
#            (c) 2010 Battelle Energy Alliance, LLC             #
#                      ALL RIGHTS RESERVED                      #
#                                                               #
#           Prepared by Battelle Energy Alliance, LLC           #
#             Under Contract No. DE-AC07-05ID14517              #
#              With the U. S. Department of Energy              #
#                                                               #
#              See COPYRIGHT for full restrictions              #
#################################################################
import os
import sys
import re
import argparse
import subprocess
import multiprocessing
import collections
import logging


import extensions
import commands
from MooseMarkdown import MooseMarkdown
from MarkdownTable import MarkdownTable
from MooseApplicationSyntax import MooseApplicationSyntax
from MooseLinkDatabase import MooseLinkDatabase

import mooseutils

# Check for the necessary packages, this does a load so they should all get loaded.
if mooseutils.check_configuration(['yaml', 'jinja2', 'markdown', 'mdx_math', 'bs4', 'lxml',
                                   'pylatexenc']):
    sys.exit(1)

import yaml #pylint: disable=wrong-import-position

MOOSEDOCS_LOG = logging.getLogger(__name__)
MOOSEDOCS_LOG.addHandler(logging.NullHandler())

MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getcwd(), '..', 'moose'))
if not os.path.exists(MOOSE_DIR):
    MOOSE_DIR = os.path.join(os.getenv('HOME'), 'projects', 'moose')

ROOT_DIR = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                   cwd=os.path.dirname(__file__),
                                   stderr=subprocess.STDOUT).strip('\n')

TEMP_DIR = os.path.abspath(os.path.join(os.getenv('HOME'), '.local', 'share', 'moose'))

class MooseDocsFormatter(logging.Formatter):
    """
    A formatter that is aware of the class hierarchy of the MooseDocs library.

    Call the init_logging function to initialize the use of this custom formatter.
    """
    COLOR = {'DEBUG':'CYAN',
             'INFO':'RESET',
             'WARNING':'YELLOW',
             'ERROR':'RED',
             'CRITICAL':'MAGENTA'}
    COUNTS = {'ERROR': multiprocessing.Value('I', 0, lock=True),
              'WARNING': multiprocessing.Value('I', 0, lock=True)}

    def format(self, record):
        msg = logging.Formatter.format(self, record)
        if record.levelname in self.COLOR:
            msg = mooseutils.colorText(msg, self.COLOR[record.levelname])

        if record.levelname in self.COUNTS:
            with self.COUNTS[record.levelname].get_lock():
                self.COUNTS[record.levelname].value += 1

        return msg

    def counts(self):
        return self.COUNTS['WARNING'].value, self.COUNTS['ERROR'].value


def abspath(*args):
    """
    Create an absolute path from paths that are given relative to the ROOT_DIR.

    Inputs:
      *args: Path(s) defined relative to the git repository root directory as defined in ROOT_DIR.
    """
    return os.path.abspath(os.path.join(ROOT_DIR, *args))


def relpath(abs_path):
    """
    Create a relative path from the absolute path given relative to the ROOT_DIR.

    Inputs:
      abs_path[str]: Absolute path that to be converted to a relative path to the git repository
                     root directory as defined in ROOT_DIR
    """
    return os.path.relpath(abs_path, ROOT_DIR)


def init_logging(verbose=False):
    """
    Call this function to initialize the MooseDocs logging formatter.
    """

    # Setup the logger object
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Custom format that colors and counts errors/warnings
    formatter = MooseDocsFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # The markdown package dumps way too much information in debug mode (so always set it to INFO)
    log = logging.getLogger('MARKDOWN')
    log.setLevel(logging.INFO)

    # Setup the custom formatter
    log = logging.getLogger('MooseDocs')
    log.addHandler(handler)
    log.setLevel(level)

    return formatter

def html_id(string):
    """
    Returns valid string for use as html id tag.
    """
    return re.sub(r'(-+)', '-', re.sub(r'[^\w]', '-', string).lower()).strip('-')

class Loader(yaml.Loader):
    """
    A custom loader that handles nested includes. The nested includes should use absolute paths
    from the origin yaml file.
    """

    def include(self, node):
        """
        Allow for the embedding of yaml files.
        http://stackoverflow.com/questions/528281/how-can-i-include-an-yaml-file-inside-another
        """
        filename = abspath(self.construct_scalar(node))
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return yaml.load(f, Loader)
        else:
            raise IOError("Unknown included file: {}".format(filename))


def yaml_load(filename):
    """
    Load a YAML file capable of including other YAML files.

    Args:
      filename[str]: The name to the file to load, relative to the git root directory
      loader[yaml.Loader]: The loader to utilize.
    """

    # Attach the include constructor to our custom loader.
    Loader.add_constructor('!include', Loader.include)

    if not os.path.exists(filename):
        raise IOError("The supplied configuration file was not found: {}".format(filename))

    with open(filename, 'r') as fid:
        yml = yaml.load(fid.read(), Loader)

    return yml

def load_config(config_file, **kwargs):
    """
    Read the MooseDocs configure file (e.g., website.yml)
    """
    out = collections.OrderedDict()
    config = yaml_load(config_file)
    for item in config:
        if isinstance(item, str):
            out[item] = dict()
        else:
            out[item.keys()[0]] = item.values()[0]

    for value in out.itervalues():
        for k, v in kwargs.iteritems():
            if k in value:
                value[k] = v
    return out

def purge(ext):
    """
    Removes generated files from repository.

    Args:
      ext[list]: List of file extensions to purge (e.g., 'png'); it will be prefixed with
                 '.moose.' so the files actually removed are '.moose.png'.
    """
    for i, ext in enumerate(ext):
        ext[i] = '.moose.{}'.format(ext)

    for root, _, files in os.walk(os.getcwd(), topdown=False):
        for name in files:
            if any([name.endswith(ext) for ext in ext]):
                full_file = os.path.join(root, name)
                MOOSEDOCS_LOG.debug('Removing: %s', full_file)
                os.remove(full_file)


def command_line_options(*args):
    """
    Return the command line options for the moosedocs script.
    """

    # Command-line options
    parser = argparse.ArgumentParser(description="Tool for building and developing MOOSE and "
                                                 "MOOSE-based application documentation.")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Execute with verbose (debug) output.")

    subparser = parser.add_subparsers(title='Commands', dest='command',
                                      description="Documentation creation command to execute.")

    # Add the sub-commands
    check_parser = subparser.add_parser('check', help="Check that the documentation exists and is "
                                                      "complete for your application and "
                                                      "optionally generating missing markdown "
                                                      "files.")
    commands.check_options(check_parser)

    build_parser = subparser.add_parser('build', help="Build the documentation for serving on "
                                                      "another system.")
    commands.build_options(build_parser)

    latex_parser = subparser.add_parser('latex', help="Generate a .tex or .pdf document from a "
                                                      "markdown file.")
    commands.latex_options(latex_parser)

    presentation_parser = subparser.add_parser('presentation', help="Convert a markdown file to "
                                                                    "an html presentation.")
    commands.presentation_options(presentation_parser)

    subparser.add_parser('test', help='Deprecated: use "~/projects/moose/python/run_tests -j8 '
                                      '--re=MooseDocs"')
    subparser.add_parser('generate', help='Deprecated: use "check --generate"')
    subparser.add_parser('serve', help='Deprecated: use "build --serve"')

    return parser.parse_args(*args)

def moosedocs():

    # Options
    options = vars(command_line_options())

    # Initialize logging
    formatter = init_logging(options.pop('verbose'))

    # Remove moose.svg files (these get generated via dot)
    MOOSEDOCS_LOG.debug('Removing *.moose.svg files from %s', os.getcwd())
    purge(['svg'])

    # Pull LFS image files
    try:
        subprocess.check_output(['git', 'lfs', 'pull'], cwd=ROOT_DIR)
    except subprocess.CalledProcessError:
        MOOSEDOCS_LOG.error("Unable to run 'git lfs', it is likely not installed but required for "
                            "the MOOSE documentation system.")
        sys.exit(1)

    # Execute command
    cmd = options.pop('command')
    if cmd == 'test':
        retcode = None
        MOOSEDOCS_LOG.error('Deprecated command, please used "~/projects/moose/python/run_tests '
                            '-j8 --re=MooseDocs" instead.')
    elif cmd == 'check':
        retcode = commands.check(**options) #pylint: disable=assignment-from-none
    elif cmd == 'generate':
        retcode = None
        MOOSEDOCS_LOG.error('Deprecated command, please used "check --generate" instead.')
    elif cmd == 'serve':
        retcode = None
        MOOSEDOCS_LOG.error('Deprecated command, please used "build --serve" instead.')
    elif cmd == 'build':
        retcode = commands.build(**options) #pylint: disable=assignment-from-none
    elif cmd == 'latex':
        retcode = commands.latex(**options) #pylint: disable=assignment-from-none
    elif cmd == 'presentation':
        retcode = commands.presentation(**options) #pylint: disable=assignment-from-none

    # Check retcode
    if retcode is not None:
        return retcode

    # Display logging results
    warn, err = formatter.counts()
    print 'WARNINGS: {}  ERRORS: {}'.format(warn, err)
    return err > 0
