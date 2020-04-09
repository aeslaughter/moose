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
window = chigger.Window(size=(300,300))
viewport = chigger.Viewport(window)
outline = chigger.geometric.Outline2D(viewport, bounds=(0, 1, 0, 1), color=(1,1,0), linewidth=5)
#window.write('outline2D.png')
window.start()
