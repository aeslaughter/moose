from sympy.vector import CoordSysCartesian
C = CoordSysCartesian('C')

from sympy import symbols
v1, v2, v3 = symbols('v1 v2 v3', type="Function")
v = v1(C.x, C.y, C.z)*C.i + v2(C.x, C.y, C.z)*C.j + v3(C.x, C.y, C.z)*C.z
