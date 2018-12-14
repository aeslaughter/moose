#!/usr/bin/env python
import chigger

reader = chigger.exodus.ExodusReader('../input/input_no_adapt_out.e')
result = chigger.exodus.ExodusResult(reader)
window = chigger.RenderWindow(result)
window.start()
