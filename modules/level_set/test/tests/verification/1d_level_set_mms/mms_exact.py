#!/usr/bin/env python
import mms
f, s = mms.evaluate('diff(u, t) + v*div(u)', 'a*t**2*sin(2*pi/b*x)', scalars=['a', 'b'], vectors=['v'])

mms.print_hit(f, 'phi_forcing', a=1, b=32)
mms.print_hit(s, 'phi_exact')
