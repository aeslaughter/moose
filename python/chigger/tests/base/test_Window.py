#!/usr/bin/env python
import chigger

window = chigger.Window(size=(1000,300), background=(1,0.2,1))
view = chigger.Viewport(window)
cube = chigger.geometric.Cube(view)
window.start()

#window.write('window.png')
