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

ax = misc.AxisSource(title='Axis Title',
                     title_position=0.75,
                     point2=(0.25, 0.25),
                     point1=(0.75, 0.75),
                     linewidth=2,
                     color=(0,0,0.8))
view = chigger.Viewport(ax)
window = chigger.Window(view, size=(600,300), background=(1,1,1))
window.write('axis.png')
window.start()
