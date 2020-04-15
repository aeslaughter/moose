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
import chigger2 as chigger

window = chigger.Window(size=(400, 400))
viewport = chigger.Viewport(window)

reader = chigger.exodus.ExodusReader('../input/step10_micro_out.e', timestep=0)
mug = chigger.exodus.ExodusSource(viewport, reader, variable='phi', cmap={'key':'viridis'}, lim=(0, 1))

times = reader.getTimes()
print(times)
for i in range(len(times)):
    reader.setParams(timestep=i)
    window.write('adapt_' + str(i) + '.png')

window.start()
