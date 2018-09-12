#!/usr/bin/env python
import vtk

# Input file and variable
filename = 'mug_blocks_outg.e'
nodal_var = 'convected'

# Read Exodus Data
reader = vtk.vtkExodusIIReader()
reader.SetFileName(filename)
reader.UpdateInformation()
reader.SetTimeStep(10)
reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1) # enables all NODAL variables
reader.Update()

# Calculator
calc = vtk.vtkArrayCalculator()
calc.SetInputConnection(reader.GetOutputPort())

# Create Geometry
geometry = vtk.vtkCompositeDataGeometryFilter()
geometry.SetInputConnection(0, calc.GetOutputPort(0))
geometry.Update()

# Mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(geometry.GetOutputPort())
mapper.SelectColorArray(nodal_var)
mapper.SetScalarModeToUsePointFieldData()
mapper.InterpolateScalarsBeforeMappingOn()

# Actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

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
