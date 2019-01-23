#!/usr/bin/env python
import vtk

filename = '../tests/input/pipe.e'
nodal_var = 'u'

reader = vtk.vtkExodusIIReader()
reader.SetFileName(filename)
reader.UpdateInformation()
reader.SetTimeStep(1)
reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1) # enables all NODAL variables
reader.Update()

geometry = vtk.vtkCompositeDataGeometryFilter()
geometry.SetInputConnection(0, reader.GetOutputPort(0))
geometry.Update()

rotate0 = vtk.vtkRotationalExtrusionFilter()
rotate0.SetInputConnection(0, geometry.GetOutputPort(0))
rotate0.SetResolution(100)

transform = vtk.vtkTransform()
transform.RotateX(90)

translate = vtk.vtkTransformPolyDataFilter()
translate.SetInputConnection(0, rotate0.GetOutputPort(0))
translate.SetTransform(transform)

rotate1 = vtk.vtkRotationalExtrusionFilter()
rotate1.SetInputConnection(0, translate.GetOutputPort(0))
rotate1.SetResolution(100)


# Mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(rotate1.GetOutputPort())
mapper.SelectColorArray(nodal_var)
mapper.SetScalarModeToUsePointFieldData()
mapper.InterpolateScalarsBeforeMappingOn()

# Actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetOpacity(0.5)

# Renderer
renderer = vtk.vtkRenderer()
renderer.AddViewProp(actor)

# Window and Interactor
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(600, 600)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

# Show the result
window.Render()
interactor.Start()
