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

from .Window import Window
from .Viewport import Viewport
from . import annotations
from . import base
from . import utils
from . import misc
from . import exodus
from . import geometric
from . import graphs
from . import filters
from . import observers

import logging
level = dict(critical=logging.CRITICAL, error=logging.ERROR, warning=logging.warning,
             info=logging.INFO, debug=logging.DEBUG, notset=logging.NOTSET)
logging.basicConfig(level=level[os.getenv('CHIGGER_LOG_LEVEL', 'INFO').lower()])
