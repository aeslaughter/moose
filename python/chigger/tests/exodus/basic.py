#!/usr/bin/env python
import chigger


window = chigger.Window()
viewport = chigger.Viewport(window)

reader = chigger.exodus.ExodusReader('../input/mug_blocks_out.e')
source = chigger.exodus.ExodusSource(viewport, reader, variable='convected')


window.start()
