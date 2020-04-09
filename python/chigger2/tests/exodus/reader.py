#!/usr/bin/env python
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
os.environ['CHIGGER_LOG_LEVEL'] = 'DEBUG'

import chigger
reader = chigger.exodus.ExodusReader('../input/mug_blocks_out.e', time=1.2345)

finfo = reader.getFileInformation()
reader.setOption('time', 1.23456)
finfo = reader.getFileInformation()

#reader.Update()
