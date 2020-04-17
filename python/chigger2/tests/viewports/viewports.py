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
a = chigger.Viewport(window, xlim=(0,0.5), ylim=(0,0.5), background=(0,0,0))
b = chigger.Viewport(window, xlim=(0.5,1), ylim=(0,0.5), background=(1,0,0))
c = chigger.Viewport(window, xlim=(0,0.5), ylim=(0.5,1), background=(0,1,0))
d = chigger.Viewport(window, xlim=(0.5,1), ylim=(0.5,1), background=(0,0,1))
window.start()
