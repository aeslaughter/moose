#!/usr/bin/env python3
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
import chigger
window = chigger.Window(size=(300, 300))
viewport0 = chigger.Viewport(window, interactive=True)
square0 = chigger.geometric.Rectangle(viewport0, bounds=(0.1, 0.9, 0.1, 0.9))
#cube0 = chigger.geometric.Cube(viewport0, bounds=(0, 1, 0, 1, 0, 1), color=(0,1,0))

#viewport1 = chigger.Viewport(window, interactive=True)
#cube1 = chigger.geometric.Cube(viewport1, bounds=(1, 2, 1, 2, 1, 2), color=(1,0,0))

window.start()
