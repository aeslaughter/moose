#!/usr/bin/env python
import vtk
import chigger
import glob

MICROSCALE_VAR = 'T'

positions = [(0.1, 0.2, 0.3),
             (-0.5, 0.0, 0.0)]

readers = []
results = []
renderer = vtk.vtkRenderer()
for i, filename in enumerate(glob.glob('mesoscale_out_particles*.e')):

    pos = [-p for p in positions[i]]
    transform0 = chigger.filters.TransformFilter(translate=pos)
    rot0 = chigger.filters.RotationalExtrusionFilter()
    transform1 = chigger.filters.TransformFilter(translate=positions[i])


    readers.append(chigger.exodus.ExodusReader(filename))
    results.append(chigger.exodus.ExodusResult(readers[-1],
                                               renderer=renderer,
                                               filters=[transform0, rot0, transform1],
                                               variable=MICROSCALE_VAR))


window = chigger.RenderWindow(*results, size=[900, 900], test=False)
window.update()
window.start()
