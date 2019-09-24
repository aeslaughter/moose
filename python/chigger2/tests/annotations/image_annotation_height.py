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
moose = chigger.annotations.ImageAnnotation(filename='../../../chigger/logos/moose.png', opacity=0.5,
                                            height=0.5, width=0.75, position=(0.5, 0.75))
window = chigger.RenderWindow(moose, size=(400,400), test=True)
window.write('image_annotation_height.png')
window.start()