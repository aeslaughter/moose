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
text = chigger.annotations.TextAnnotation(name='text', text='This is a test.')
text.setOptions(font_size=32)

#, font_size=32,
#                                          text_color=(1.,0.,1.), text_opacity=0.5, layer=0)

window = chigger.RenderWindow(text, size=(1000,1000), test=False)
window.start()
