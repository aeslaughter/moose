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

left = chigger.Viewport(window, viewport=(0, 0, 0.5, 1), highlight=True)
right = chigger.Viewport(window, viewport=(0.5, 0, 1, 1), highlight=True)
window.write(filename='highlight_on.png')
right.setOptions(highlight=False)
window.write(filename='highlight_off.png')
window.start()
