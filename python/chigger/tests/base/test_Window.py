#!/usr/bin/env python
import chigger

window = chigger.Window(size=(1000,300), background=(0,0.2,1))
obs = chigger.observers.MainWindowObserver(window)
view = chigger.Viewport(window)
cube = chigger.geometric.Cube(view)
window.write('window.png')
window.start()
