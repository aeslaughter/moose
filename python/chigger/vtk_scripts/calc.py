#!/usr/bin/env python
import vtk

# Input file and variable
filename = 'mug_blocks_out.e'
nodal_var = 'convected'

# Read Exodus Data
reader = vtk.vtkExodusIIReader()
reader.SetFileName(filename)
reader.UpdateInformation()
reader.SetTimeStep(10)
reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
reader.Update()

# Calculator
calc = vtk.vtkArrayCalculator()
calc.SetInputConnection(reader.GetOutputPort())
calc.AddScalarArrayName(nodal_var)
calc.SetFunction(nodal_var + "+2")
calc.SetResultArrayName('foo')

calc.Update()
print calc.GetOutput(0)

# Create Geometry
geometry = vtk.vtkCompositeDataGeometryFilter()
geometry.SetInputConnection(0, calc.GetOutputPort(0))
geometry.Update()

# Mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(geometry.GetOutputPort())
mapper.SelectColorArray('foo')
#mapper.SetScalarRange([2, 3])
mapper.SetScalarModeToUsePointFieldData()
mapper.InterpolateScalarsBeforeMappingOn()


mapper.Update()
print mapper.GetScalarRange() # seems like this should be [2,3]

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
