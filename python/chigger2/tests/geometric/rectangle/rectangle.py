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

import vtk
import chigger
import numpy as np

window = chigger.Window(size=(500,300), background=(1,0.2,1))
view = chigger.Viewport(window)

n = 1000
m = 1

ydata = np.linspace(0, 1, n+1)
data = vtk.vtkFloatArray()
data.SetName('data')
data.SetNumberOfTuples((n+1)*(m+1))
idx = 0
for i in range(n+1):
    for j in range(m+1):
        data.SetValue(idx, 1-ydata[i])
        idx += 1

rect = chigger.geometric.Rectangle(view, cmap='viridis',
                                   bounds=(100, 200, 100, 200),
                                   #origin=(100, 100, 0),
                                   #point1=(150, 100, 0),
                                   #point2=(100, 200, 0),
                                   #origin=(0.25, 0.25, 0),
                                   #point1=(0.25, 0.75, 0),
                                   #point2=(0.3, 0.25, 0),
                                   resolution=(n,1),
                                   #color=(1,0,0),
                                   linewidth=2,
                                   cmap_reverse=True,
                                   rotate=45,
                                   #cmap_range=(0,0.5),
                                   coordinate_system='viewport',
                                   point_data=data)

#window.write('rectangle.png')
window.start()
