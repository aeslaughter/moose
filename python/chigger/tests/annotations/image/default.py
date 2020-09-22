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

window = chigger.Window(size=(300,600), filename='default.png')
viewport = chigger.Viewport(window)
moose = chigger.annotations.Image(viewport, width=1, valign='center', position=(0., 0.5), filename='../../../logos/moose.png')

window.write()
window.start()
