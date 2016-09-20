#!/usr/bin/env python
import chigger
import vtk

# Read the results
filename = 'johansson_vortex_out.e'
reader = chigger.ExodusReader(filename)

# Load the initial condition for display purposes
initial = chigger.ExodusReader(filename, adaptive=False, timestep=0)
initial.Update()

# Camera
camera = vtk.vtkCamera()
camera.SetViewUp(0.0000, 1.0000, 0.0000)
camera.SetPosition(0.6232, 0.4843, 2.2579)
camera.SetFocalPoint(0.6232, 0.4843, 0.0000)

# Volume Renderer
result = chigger.ExodusResult(reader, variable='phi', viewport=[0, 0, 0.6, 1], cmap='BrBG', range=[-0.5,0.5], camera=camera)
result.SetOptions('time_annotation', visible=True)
levelset = chigger.ExodusResult(reader, variable='phi', viewport=[0, 0, 0.6, 1], layer=2, camera=camera)
levelset.SetOptions('colorbar', visible=False)
levelset.SetOptions('contour', visible=True, levels=[0])

ic = chigger.ExodusResult(initial, camera=camera, viewport=[0, 0, 0.6, 1], layer=2)
ic.SetOptions('colorbar', visible=False)
ic.SetOptions('contour', visible=True, levels=[0])
ic.Update()

# Axes for displaying area Postprocessor
axes = chigger.graphs.Graph(viewport=[0.6, 0, 1, 1])
axes.SetOptions('xaxis', lim=[0,1], num_ticks=5, title='time'),
axes.SetOptions('yaxis', num_ticks=7, title='Area'),
axes.SetOptions('legend', vertical_alignment='top')
axes.AddLinePlot('ls_area', color=[0,0,1], label='LevelSetVolume')
axes.AddLinePlot('aux_area', color=[0,1,1], label='ElementAverageValue')

# Setup the window
window = chigger.RenderWindow(ic, result, levelset, axes)
window.Initialize()
window.Update()

# Update callback
def function(*args, **kwargs):
    timestep = kwargs.pop('timestep', -1)

    reader.Update(timestep=timestep)
    result.Update()
    levelset.Update()

    t = reader.GetTime()
    print 'time =', t

    a = reader.GetCurrentFieldData()
    axes.AppendLinePlot('ls_area', t, a['ls_area'])
    axes.AppendLinePlot('aux_area', t, a['aux_area'])

    window.Update()


n = len(reader.GetTimes())
for i in range(n):
    function(timestep=i)

window.Start(timer=True, function=function, milliseconds=1000)
result.PrintCamera()
