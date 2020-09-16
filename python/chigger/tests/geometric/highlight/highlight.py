#!/usr/bin/env python3
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import chigger
window = chigger.Window(size=(300, 300))
viewport = chigger.Viewport(window)
cube = chigger.geometric.Cube(viewport, bounds=(0.5, 0.8, 0, 0.5, 0.8, 1), color=(0.1, 0.2, 0.8))
highlight = chigger.geometric.Highlight(viewport, cube, offset=0.05, color=(1,0,0))

window.write(filename='highlight.png')
window.start()
