#!/usr/bin/env python
import vtk

source = vtk.vtkTextSource()
source.SetText('Testing...')
source.BackingOff()

mapper = vtk.vtkPolyDataMapper2D()
mapper.SetInputConnection(source.GetOutputPort())
mapper.ScalarVisibilityOff()


actor = vtk.vtkActor2D()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1,0.2,0.1)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

# Window and Interactor
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(400, 400)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

# Show the result
window.Render()
interactor.Start()
