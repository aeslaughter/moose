#!/usr/bin/env python
import vtk
import chigger

camera = vtk.vtkCamera()
camera.SetViewUp(0.0000000000, 1.0000000000, 0.0000000000)
camera.SetPosition(0.1520000000, 0.0128500000, 0.3251647185)
camera.SetFocalPoint(0.1520000000, 0.0128500000, 0.0000000000)

reader = chigger.exodus.ExodusReader('step1_out.e')
pressure = chigger.exodus.ExodusResult(reader, camera=camera, variable='pressure', cmap='viridis')
cbar = chigger.exodus.ExodusColorBar(pressure,
                                     length=0.6,
                                     colorbar_origin=[0.2, 0.7],
                                     location='top')
cbar.setOptions('primary', title='Pressure (Pa)', font_size=48, font_color=[0,0,0])

window = chigger.RenderWindow(pressure, cbar, size=[1920, 1080], background=[1,1,1])
window.write('step01_result.png')
window.start()
