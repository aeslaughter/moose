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
colorbar = chigger.misc.ColorBar(cmap='viridis')
colorbar.setOptions('primary', lim=(5,10))
colorbar.setOptions('secondary', lim=(100,500), visible=True)
window = chigger.RenderWindow(colorbar, size=(600,400), test=False)
window.write('colorbar.png')
window.start()

"""
plane0 = chigger.geometric.PlaneSource2D(origin=(479,100,0),
                                         point1=(509,100,0),
                                         point2=(479,299,0))

result = chigger.base.ChiggerResult(plane0)
window = chigger.RenderWindow(result, size=(600,400), test=False)
window.write('plane_source.png')
window.start()
"""
