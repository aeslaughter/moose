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
import mooseutils
import logging
log = logging.getLogger(__name__)

from .. import common
import MooseDocs


def check_options(parser):
    """
    Command-line options for check command.
    """
    parser.add_argument('--config-file', type=str, default='website.yml', help="The configuration file to use for building the documentation using MOOSE. (Default: %(default)s)")
    parser.add_argument('--locations', nargs='+', help="List of locations to consider, names should match the keys listed in the configuration file.")
    parser.add_argument('--generate', action='store_true', help="When checking the application for complete documentation generate any missing markdown documentation files.")

def check(config_file=None, locations=None, generate=None):
    """
    Performs checks and optionally generates stub pages for missing documentation.
    """
    # Read the configuration
    config = MooseDocs.load_config(config_file)
    _, ext_config = MooseDocs.get_markdown_extensions(config)
    ext_config = ext_config['MooseDocs.extensions.app_syntax']

    # Run the executable
    exe = MooseDocs.abspath(ext_config['executable'])
    if not os.path.exists(exe):
        raise IOError('The executable does not exist: {}'.format(exe))
    else:
        log.debug("Executing {} to extract syntax.".format(exe))
        raw = mooseutils.runExe(exe, '--yaml')
        yaml = mooseutils.MooseYaml(raw)

    # Populate the syntax
    for loc in ext_config['locations']:
        for key, value in loc.iteritems():
            if (locations == None) or (key in locations):
                value['group'] = key
                syntax = common.MooseApplicationSyntax(yaml, generate=generate, install=ext_config['install'], **value)
                log.info("Checking documentation for '{}'.".format(key))
                syntax.check()

    return None
