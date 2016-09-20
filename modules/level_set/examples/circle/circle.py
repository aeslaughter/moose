#!/usr/bin/env python
import vtk
import chigger
import math
import pandas

# Define the results
exodus_file = 'circle_out.e'
csv_file = 'circle_out.csv'
radius = 0.15

# Read the Exodus result
reader = chigger.ExodusReader(exodus_file)

# Shared camera from variable and contour
camera = vtk.vtkCamera()
camera.SetViewUp(0.0000, 1.0000, 0.0000)
camera.SetPosition(0.5022, 0.5672, 2.2579)
camera.SetFocalPoint(0.5022, 0.5672, 0.0000)

# Create colormap of level set variable
result = chigger.ExodusResult(reader, cmap='viridis', variable='phi', range=[-0.2, 0.5], camera=camera)# viewport=[0,0,0.5,1])
result.SetOptions('colorbar', location='top', position=[0.085,0.87], width=0.03, length=0.825)
result.SetOptions('edge', visible=True, color=[0.2, 0.2, 0.2])

# Create the levelset contour
levelset = chigger.ExodusResult(reader, variable='phi', layer=2, camera=camera, color=[0,0,0])#viewport=[0,0,0.5,1]
levelset.SetOptions('colorbar', visible=False)
levelset.SetOptions('contour', visible=True, levels=[0])

"""
# Create the line for the exact area
times = reader.GetTimes()
a = math.pi*0.15*0.15
exact = chigger.graphs.Line([times[0], times[-1]], [a,a], label='Exact', color=[1,1,1])

# Create the computed area line
csv = pandas.read_csv(csv_file)
x = csv['time']
y = csv['area']
computed = chigger.graphs.Line(label='Area', color=[0,1,0], append=False)

# Create the graph axes
graph = chigger.graphs.Graph(computed, exact, viewport=[0.5,0,1,1])
graph.SetOptions('xaxis', title='Time', lim=[x.min(), x.max()])
graph.SetOptions('yaxis', title='Area', lim=[y.min(), y.max()])
"""

# Setup the window
window = chigger.RenderWindow(result, levelset, size=[500, 500])

# Loop through the timesteps and plot the data
n = reader.GetNumberOfTimeSteps()
for i in range(n):
    reader.SetOptions(timestep=i)
    #computed.UpdateData(x[:i], y[:i])
    window.Update()
    window.Write('circle_{:03d}.png'.format(i))
window.Start()

result.PrintCamera()
