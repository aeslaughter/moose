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

k = chigger.graphs.Line([1,2,3,4], [1,2.75,3.5,4], label='k')

graph = chigger.graphs.Graph(k, legend={'visible':False})
graph.setOptions('xaxis', title='X-Axis', lim=(1,4))
graph.setOptions('yaxis', title='y-Axis', lim=(1,4))

window = chigger.RenderWindow(graph, size=(300,300), test=True)
window.write('graph.png')
window.start()
