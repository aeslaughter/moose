#!/usr/bin/env python
import chigger
import time
import numpy as np

epsilon = 0.03125
filename = 'bubble_out.e'

# Read ExodusII File
reader = chigger.ExodusReader(filename, timestep=0)

# Volume renderer
result = chigger.ExodusResult(reader, variable='phi', cmap='plasma', mesh=True)
result.SetOptions('time_annotation', visible=True)

contour = chigger.ExodusResult(reader, variable='phi', color=[0,0,0], contour={'visible':True, 'levels':[0.5]}, colorbar={'visible':False})

window = chigger.RenderWindow(result, contour, size=[1920, 1080])

n = reader.GetNumberOfTimeSteps()
for i in range(n):
    reader.SetOptions(timestep=i)
    result.Update()
    contour.Update()
    window.Update()
    print 'time =', reader.GetTime()
    time.sleep(0.4)

    if i == 0:
        contour.SetOptions(camera=result.GetCamera())

def function(*args, **kwargs):
    reader.SetOptions(timestep=-1)
    result.Update()
    contour.Update()
    window.Update()
    print 'time =', reader.GetTime()


window.Start(timer=True, function=function, timeout=2000)
