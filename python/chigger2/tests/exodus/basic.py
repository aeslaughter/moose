#!/usr/bin/env python
import vtk
import chigger2 as chigger

camera = vtk.vtkCamera()
camera.SetViewUp(0.33406544, 0.57147319, 0.74954564)
camera.SetPosition(-8.68100281, -8.16541072, 10.21956389)
camera.SetFocalPoint(0.00000000, 0.00000000, 0.12500000)

window = chigger.Window(size=(400, 400))
viewport = chigger.Viewport(window, camera=camera)
reader = chigger.exodus.ExodusReader('../input/mug_blocks_out.e')
source = chigger.exodus.ExodusSource(viewport, reader, variable='diffused', cmap={'key':'viridis'})

window.start()
