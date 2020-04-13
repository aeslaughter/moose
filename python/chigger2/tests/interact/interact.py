#!/usr/bin/env python
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

"""
This example tests the various modes of interaction available in chigger: None, native VTK, or
custom interaction (default).
"""
import argparse
import chigger2 as chigger

parser = argparse.ArgumentParser(description='Chigger interactive example and test')
parser.add_argument('--mode', type=str, default=None, help='The interaction mode.', choices=['offscreen', 'vtk', 'none', 'chigger'])
parser.add_argument('--create-main-window-observer', action='store_true', help='Toggle the auto creation of MainWindowObserver')
args = parser.parse_args()

window = chigger.Window(size=(800, 800), mode=args.mode)
#chigger.observers.MainWindowObserver(window)

left = chigger.Viewport(window, viewport=(0, 0, 0.5, 1))
right = chigger.Viewport(window, viewport=(0.5, 0, 1, 1))

#rect0 = chigger.geometric.Rectangle(left, bounds=(0.25, 0.5, 0.25, 0.75), color=(0.5, 0.1, 0.2))
cube0 = chigger.geometric.Cube(left, bounds=(0.5, 0.8, 0, 0.5, 0.8, 1), color=(0.1, 0.2, 0.8))

#rect1 = chigger.geometric.Rectangle(right, bounds=(0.25, 0.5, 0.25, 0.75), color=(0.2,0.1, 0.5))
cube1 = chigger.geometric.Cube(right, bounds=(0.5, 0.8, 0, 0.5, 0.8, 1), color=(0.8, 0.2, 0.1))

window.write('outline.png')
window.start()
