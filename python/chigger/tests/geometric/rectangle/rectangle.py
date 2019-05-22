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

import vtk
import chigger
import numpy as np

n = 50
m = 50

xdata = np.linspace(0, 1, n+1)
ydata = np.linspace(0, 1, m+1)



data = vtk.vtkFloatArray()
data.SetName('data')
data.SetNumberOfTuples((n+1)*(m+1))
idx = 0
for i in range(n+1):
    for j in range(m+1):
        data.SetValue(idx, 1-ydata[i])
        idx += 1

rect = chigger.geometric.Rectangle(origin=(0.25, 0.25, 0),
                                   point1=(0.25, 0.75, 0),
                                   point2=(0.75, 0.25, 0),
                                   resolution=(n,m),
                                   #color=(1,0,0),
                                   linewidth=2,
                                   cmap='viridis',
                                   point_data=data)

result = chigger.Viewport(rect)
window = chigger.Window(result, size=(300,300), background=(1,0.5,1))
window.write('rectangle.png')
window.start()
