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

reader = chigger.exodus.ExodusReader('../input/step10_micro_out.e', timestep=0)
mug = chigger.exodus.ExodusSource(viewport, reader, variable='phi', cmap='viridis', lim=(0, 1))

times = reader.getTimes()
for i in range(len(times)):
    reader.setOptions(timestep=i)
    window.write(filename='adapt_' + str(i) + '.png')

window.start()
