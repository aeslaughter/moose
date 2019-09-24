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
from chigger import geometric

box0 = geometric.CubeSource(center=(0.5,0.5,0.5), lengths=(1.,1.,1.), color=(0.25,0.5,0.75))
                                    #opacity=0.5, edges=True, edge_color=(1,1,1))
box1 = geometric.CubeSource(center=(0.25,0.25,0.25), lengths=(3.,2.,1.), color=(1,0.5,0.5))

geo = geometric.GeometricResult(box0, box1)

window = chigger.RenderWindow(geo, size=(300,300))

obs = chigger.observers.MainWindowObserver(window)

window.write('cube_source.png')
window.start()
