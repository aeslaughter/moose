ls #!/usr/bin/env python2
#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import chigger
#reader = chigger.exodus.ExodusReader('../input/step10_micro_out.e', time=2.2)
reader = chigger.exodus.ExodusReader('../input/mug_blocks_out.e', time=1.2345)
reader.Update()
