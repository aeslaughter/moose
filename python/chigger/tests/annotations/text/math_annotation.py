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
window = chigger.Window(size=(300,300), filename='math_annotation.png')
viewport = chigger.Viewport()
text = chigger.annotations.Text(text='$\\rho C_p\\frac{\\partial T}{\\partial t} - \\nabla\\cdot(k\\nabla T) = s$',
                                position=(0.5, 0.5), size=18, halign='center', valign='center')
window.write()
window.start()
