#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import os
import logging
import mooseutils

class ChiggerFormatter(logging.Formatter):
    """
    A formatter that is aware of the class hierarchy of the MooseDocs library.
    Call the init_logging function to initialize the use of this custom formatter.

    TODO: ChiggerFormatter or something similar (MooseDocsFormatter) should be used by all
          moosetools as should be the logging methods in ChiggerObject.

          Perhaps a "mixins" package: 'moosetools.mixins.MooseLoggerMixin' would add the log methods,
          other objects such at the AutoProperty would also go within that module
    """
    COLOR = dict(DEBUG='CYAN',
                 INFO='RESET',
                 WARNING='LIGHT_YELLOW',
                 ERROR='LIGHT_RED',
                 CRITICAL='LIGHT_MAGENTA')

    COUNTS = dict(CRITICAL=0, ERROR=0, WARNING=0, INFO=0, DEBUG=0)

    def format(self, record):
        """Format the supplied logging record and count the occurrences."""
        self.COUNTS[record.levelname] += 1

        msg = '{} {}:{} {}\n'.format(mooseutils.colorText(record.levelname, self.COLOR[record.levelname]),
                                     mooseutils.colorText(record.name, 'LIGHT_GREY') ,
                                     mooseutils.colorText(str(record.lineno), 'LIGHT_GREY'),
                                     logging.Formatter.format(self, record))
        return msg

# Setup the logging
level = dict(critical=logging.CRITICAL, error=logging.ERROR, warning=logging.warning,
             info=logging.INFO, debug=logging.DEBUG, notset=logging.NOTSET)

formatter = ChiggerFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)

log = logging.getLogger('')
log.addHandler(handler)
log.setLevel(level[os.getenv('CHIGGER_LOG_LEVEL', 'INFO').lower()])

from .Window import Window
from .Viewport import Viewport, Background
from . import annotations
from . import base
from . import utils
from . import misc
from . import exodus
from . import geometric
from . import graphs
from . import filters
from . import observers
