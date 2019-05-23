#!/usr/bin/env python2
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
from chigger import misc, observers

cb = misc.ColorBar(rotate=0)
view = chigger.Viewport(cb)
window = chigger.Window(view, size=(1200, 600), background=(1,1,1))
window.write('colorbar.png')
window.start()
