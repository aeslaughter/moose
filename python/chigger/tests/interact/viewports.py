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
window = chigger.Window(size=(800, 800))
chigger.observers.MainWindowObserver(window)

a = chigger.Viewport(window, viewport=(0, 0, 0.5, 0.5))
b = chigger.Viewport(window, viewport=(0.5, 0, 1, 0.5))
c = chigger.Viewport(window, viewport=(0.5, 0.5, 1, 1))
d = chigger.Viewport(window, viewport=(0, 0.5, 0.5, 1))

window.start()
