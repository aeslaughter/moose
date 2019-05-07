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

ax0 = misc.AxisSource(title='Axis Title', fontcolor=(0,1,0))
result0 = chigger.Viewport(ax0)
window = chigger.Window(result0, size=(600,300), background=(1,1,1))

obs = observers.MainWindowObserver(window)

window.write('axis.png')
window.start()
