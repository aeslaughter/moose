#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import os
import platform
import logging
#import mooseutils
import packaging.version
from moosetools import mooseutils
from moosetools import moosetest


class ValgrindRunController(moosetest.base.Controller):
    """
    A `Controller` for running with Valgrind.
    """
    AUTO_BUILD = False

    @staticmethod
    def validParams():
        params = moosetest.base.Controller.validParams()
        params.setValue('prefix', 'valgrind')
        return params

    @staticmethod
    def validObjectParams():
        """
        Return an `parameters.InputParameters` object to be added to a sub-parameter of an object
        with the name given in the "prefix" parameter
        """
        params = moosetest.base.Controller.validObjectParams()
        #params.add('ad_mode', allow=('SPARSE', 'NONSPARSE', 'sparse', 'nonsparse'), vtype=str,
        #           doc="Limit the test to a specific automatic differentiation derivative type.")
        return params

    @staticmethod
    def validCommandLineArguments(parser, params):
        return parser


    def execute(self, obj, params):
        pass
