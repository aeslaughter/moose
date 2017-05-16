#pylint: disable=missing-docstring
####################################################################################################
#                                    DO NOT MODIFY THIS HEADER                                     #
#                   MOOSE - Multiphysics Object Oriented Simulation Environment                    #
#                                                                                                  #
#                              (c) 2010 Battelle Energy Alliance, LLC                              #
#                                       ALL RIGHTS RESERVED                                        #
#                                                                                                  #
#                            Prepared by Battelle Energy Alliance, LLC                             #
#                               Under Contract No. DE-AC07-05ID14517                               #
#                               With the U. S. Department of Energy                                #
#                                                                                                  #
#                               See COPYRIGHT for full restrictions                                #
####################################################################################################
#pylint: enable=missing-docstring
import logging

import MooseDocs
from MooseDocs.extensions.app_syntax import AppSyntaxExtension

LOG = logging.getLogger(__name__)

def check_options(parser):
    """
    Command-line options for check command.
    """
    parser.add_argument('--config-file', type=str, default='website.yml',
                        help="The configuration file to use for building the documentation using "
                             "MOOSE. (Default: %(default)s)")
    parser.add_argument('--template', type=str, default='website.html',
                        help="The template html file to utilize (default: %(default)s).")
    parser.add_argument('--generate', action='store_true',
                        help="When checking the application for complete documentation generate "
                             "any missing markdown documentation files.")
    parser.add_argument('--dump', action='store_true',
                        help="Dump the complete MooseDocs syntax tree to the screen.")


def check(config_file=None, generate=None, dump=None, template=None, **template_args):
    """
    Performs checks and optionally generates stub pages for missing documentation.
    """

    # Create the markdown parser and get the AppSyntaxExtension
    config = MooseDocs.load_config(config_file, template=template, template_args=template_args)
    parser = MooseDocs.MooseMarkdown(config)
    ext = parser.getExtension(AppSyntaxExtension)
    syntax = ext.getMooseAppSyntax()

    # Dump the complete syntax tree if desired
    if dump:
        print syntax

    # Check all nodes for documentation
    for node in syntax.findall():
        node.check(ext.getConfig('install'), generate)

    return None
