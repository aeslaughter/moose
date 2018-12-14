#!/usr/bin/env python
import vtk
import mooseutils
import chigger


variable = 'u'
rng = [0, 14]
filename = '../input/input_no_adapt_out.e'

reader = chigger.exodus.ExodusReader(filename, time=2)
result = chigger.exodus.ExodusResult(reader)
result.setOptions('edges', visible=True)
window = chigger.RenderWindow(result)
window.start()


"""
# Window and Interactor
window = vtk.vtkRenderWindow()
window.AddRenderer(result.getVTKRenderer())
window.SetSize(600, 600)
#
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()
#
### Show the result
window.Render()
interactor.Start()
"""
