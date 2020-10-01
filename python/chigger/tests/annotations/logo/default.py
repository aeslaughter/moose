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
viewport = chigger.Viewport()
chigger.annotations.Logo(logo='inl', position=(0.5, 0.5), width=0.33, halign='center', valign='center')
chigger.annotations.Logo(logo='moose', position=(0, 0), width=0.33, halign='left', valign='bottom')
chigger.annotations.Logo(logo='marmot_green', position=(0, 1), width=0.33, halign='left', valign='top')
chigger.annotations.Logo(logo='pika_white', position=(1, 1), width=0.33, halign='right', valign='top')
chigger.annotations.Logo(logo='chigger_white', position=(1., 0.), width=0.33, halign='right', valign='bottom')

window.write(filename='default.png')
window.start()
