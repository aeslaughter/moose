import argparse
import logging

from commands import build
#import common
#import extensions


logging.basicConfig()

def command_line_options():
    parser = argparse.ArgumentParser(description="Utility for build MOOSE documentation.")
    subparser = parser.add_subparsers(help='Available commands.')
    build.command_line_options(subparser)

    return parser.parse_args()

def main():

    options = command_line_options()
    print options
    pass

if __name__ == '__main__':
    main()
