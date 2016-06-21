#!/usr/bin/env python
import os
import utils
import logging
from mkdocs.commands import serve, build
import MooseDocs
import argparse


import inspect

class MkMooseDocsFormatter(logging.Formatter):

    COLOR = {'DEBUG':'GREEN', 'INFO':'RESET', 'WARNING':'YELLOW', 'ERROR':'RED', 'CRITICAL':'MAGENTA'}

    def format(self, record):
        return logging.Formatter.format(self, record)

        """
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        print("  I was called by {}.{}()".format(str(the_class), the_method))

        msg = logging.Formatter.format(self, record)

        indent = record.name.count('.')

        if record.levelname in ['WARNING', 'ERROR', 'CRITICAL']:
            msg = '{}{}: {}'.format(' '*4*indent, record.levelname, msg)
        else:
            msg = '{}{}'.format(' '*4*indent, msg)

        if record.levelname in self.COLOR:
            msg = utils.colorText(msg, self.COLOR[record.levelname])

        return msg
        """



if __name__ == '__main__':



    # Command-line options
    parser = argparse.ArgumentParser(description="Tool for building and developing MOOSE and MOOSE-based application documentation.")
    parser.add_argument('docs_dir', type=str, nargs='?', default=os.getcwd(), help="The 'docs' directory where the markdown for the site resides.")
    parser.add_argument('--root', '-r', type=str, default=os.path.abspath('..'), help="The root directory of the application. (Default: %(default)s)")
    parser.add_argument('--config-file', '-c', type=str, default=os.path.join('mkdocs.yml'), help="The configuration file to use for building the documentation. (Default: %(default)s)")
    #parser.add_argument('--executable', '-e', type=str, help="The MOOSE application executable to use for generating documentstion. If a directory is supplied it wil be searched for an executable, if nothing is provided the current working directory (cwd) is searched.")

    subparser = parser.add_subparsers(title='Commands', description="Documenation creation command to execute.", dest='command')

    generate_parser = subparser.add_parser('generate', help="Generate the markdown documentation from MOOSE application executable.")

    serve_parser = subparser.add_parser('serve', help='Sever the documentation using a local server.')
    serve_parser.add_argument('--no-livereload', action='store_true', help="Disable the live reloading of the served site.")
    serve_parser.add_argument('--no-generate', action='store_true', help="Disable the documentation generation prior to serving.")
    serve_parser.add_argument('--strict', action='store_true', help='Enable strict mode and abort on warnings.')
    #serve_parser.add_argument('--develop', action='store_true', help="Enable generation even if the executable does not change.")


    options = parser.parse_args()

    # Setup the logger object
    logging.basicConfig(level=logging.INFO)
    #log = logging.getLogger('MooseDocs')
    """
    formatter = MkMooseDocsFormatter()#'%(name)s:%(levelname)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    """
    #log.setLevel(logging.DEBUG)

    # Working directory
    if not os.path.isdir(options.root):
        raise IOError("The supplied root directory is not valid: {}".format(options.root))

    """
    # Executable
    if not options.executable:
        options.executable = utils.find_moose_executable(options.root)
    elif os.path.isdir(options.executable):
        options.executable = utils.find_moose_executable(options.executable)

    if not os.path.exists(options.executable):
        raise IOError("Unable to locate a valid MOOSE application executable in '{}'".format(options.executable))

    if not os.path.isabs(options.executable):
        options.executable = os.path.abspath(options.executable)
    """

    # Configuration file
    if not os.path.isabs(options.config_file):
        options.config_file = os.path.join(options.docs_dir, options.config_file)

    if not os.path.exists(options.config_file):
        raise IOError("The supplied configuation file was not found: {}".format(options.config_file))

    # GENERATE:
    if options.command == 'generate':
        gen = MooseDocs.MooseApplicationDocGenerator(options.config_file)
        gen()

    # SERVE:
    elif options.command == 'serve':

        if not options.no_generate:
            gen = MooseDocs.MooseApplicationDocGenerator(options.config_file)
            gen()

        serve.serve(config_file=options.config_file, strict=options.strict, livereload=(not options.no_livereload))
