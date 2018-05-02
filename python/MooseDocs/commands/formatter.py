#pylint: disable=missing-docstring, no-member
import os
import logging

from MooseDocs import common

def command_line_options(subparser, parent):
    """Define the 'format' command."""

    parser = subparser.add_parser('format',
                                  parents=[parent],
                                  help='Tool for profiling MooseDocs performance.')
    parser.add_argument('--config', default='config.yml', help="The configuration file.")
    parser.add_argument('--destination',
                        default=os.path.join(os.getenv('HOME'), '.local', 'share', 'moose', 'site'),
                        help="Destination for writing build content.")

    parser.add_argument('-f', '--files', default=[], nargs='*',
                        help="A list of file to build, this is useful for testing. The paths " \
                             "should be as complete as necessary to make the name unique, just " \
                             "as done within the markdown itself.")

    #parser.add_argument('-t', '--tokenize', action='store_true',
    #                    help="Enable profiling of tokenization.")
   # parser.add_argument('-r', '--render', action='store_true',
    #                    help="Enable profiling of rendering.")

def main(options):
    """./moosedocs.py format"""

    log = logging.getLogger(__name__)


    translator, _ = common.load_config(options.config, Renderer={'type':'MooseDocs.base.MooseDownRenderer'})
    translator.init(options.destination)

    core = translator.root.findall('format.md')[0]
    core.build()
#    print core.ast
    print core.result
