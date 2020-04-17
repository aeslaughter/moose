#!/usr/bin/env python
import chigger2 as chigger

window = chigger.Window(size=(300,300))
view0 = chigger.Viewport(window, background=(0,0.2,1), viewport=(0, 0, 0.5, 1))
view1 = chigger.Viewport(window, background=(0.2,0,0.2), viewport=(0.5, 0, 1, 1))
window.write('viewport.png')
window.start()
