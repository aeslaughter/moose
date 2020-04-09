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

import chigger
left = chigger.Viewport(background=(0,1,0), background2=(1,0,0), viewport=(0,0,0.5,1), layer=0)
right = chigger.Viewport(background=(0.5,0.5,0.85), viewport=(0.5,0,1,1), layer=0)

box = chigger.geometric.CubeSource(center=(0.5,0.5,0.5), lengths=(1.,1.,1.), color=(0.25,0.5,0.75))
view = chigger.Viewport(box, layer=1)

window = chigger.Window(right, left, view, size=(300,300))
window.write('dual.png')
window.start()
