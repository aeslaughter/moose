cp#!/usr/bin/env python
import chigger
import time
import numpy as np

epsilon = 0.0625
filename = 'bubble_out.e'

# Read ExodusII File
reader = chigger.ExodusReader(filename, timestep=0)

# Volume renderer
result = chigger.ExodusResult(reader, viewport=[0,0,0.5,1], variable='phi', cmap='plasma', mesh=True)
result.SetOptions('time_annotation', visible=True)

# Sample the data
p0 = (0, 0.5, 0)
p1 = (1, 0.5, 0)
sample = chigger.samplers.ExodusLineSampler(result, p0, p1, resolution=200)
x = sample.GetDistance()

x0 = np.arange(0, 1, 0.01)
y0 = 1 / (1+np.exp((x0-0.5)/epsilon))

# Exodus field data graph
phi = chigger.graphs.Line(label='phi', color=[1,0,0], append=False)
phi_exact = chigger.graphs.Line(x0, y0, label='phi_exact', color=[0,0,1], append=False)
chart = chigger.graphs.Graph(phi, phi_exact, viewport=[0.5, 0, 1, 1],
                             xaxis={'lim':[0,1], 'num_ticks':5, 'title':'x'},
                             yaxis={'lim':[0,1], 'num_ticks':5, 'title':'phi'},
                             legend={'vertical_alignment':'center', 'horizontal_alignment':'left'})

window = chigger.RenderWindow(result, chart, size=[1920, 1080])

def function():
    n = reader.GetNumberOfTimeSteps()
    for i in range(n):
        reader.SetOptions(timestep=i)
        phi.UpdateData(x, sample.GetSample('phi'))
        window.Update()

        print 'time =', reader.GetTime()
        time.sleep(0.4)

window.Start(function=function)
