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
text = chigger.annotations.Text(text='This is a test.', orientation=45, valign='middle',
                                halign='center', position=(0.5, 0.5))
vp = chigger.Viewport(text)
window = chigger.Window(vp, size=(300,300), background=(1,1,1))
window.write('text_annotation.png')
window.start()
