"""
Main program for running MooseDocs. The moosedocs.py script that exists within the
documentation directory for applications call this in similar fashion to
MOOSE run_tests.
"""
import argparse
import logging

from commands import build, devel

#TODO: Create colored and counted logging messages.
logging.basicConfig()

def command_line_options():
    """
    The main command line parser, this creates the main parser and calls the
    calls the command_line_options method for each command.
    """
    desc = "MooseDocs: A utility to build MOOSE documentation from a single source."
    parser = argparse.ArgumentParser(description=desc)
    subparser = parser.add_subparsers(dest='command', help='Available commands.')

    build.command_line_options(subparser)
    devel.command_line_options(subparser)

    return parser.parse_args()

def main():
    """
    Parse the command line options and run the correct command.
    """
    options = command_line_options()
    if options.command == 'build':
        build.main(options)
    elif options.command == 'devel':
        devel.main(options)


if __name__ == '__main__':
    main()
