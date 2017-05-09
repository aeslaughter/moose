#!/usr/bin/env python
import chigger
filename = 'grain_growth_2D_graintracker_out.e'
reader = chigger.exodus.ExodusReader(filename)
result = chigger.exodus.ExodusResult(reader, edges=True)
window = chigger.RenderWindow(result)
window.start(timer=chigger.base.ChiggerTimer(window, duration=100))
