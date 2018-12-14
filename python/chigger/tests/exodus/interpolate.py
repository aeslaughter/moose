#!/usr/bin/env python
import chigger

filename = '../input/input_no_adapt_out.e'
reader = chigger.exodus.ExodusReader(filename, timestep=1)
print reader.getTimes()
result = chigger.exodus.ExodusResult(reader, lim=(0,4))
result.setOptions('edges', visible=True)
window = chigger.RenderWindow(result, size=(300, 300))
window.write('interpolate_2.png')
window.start()
