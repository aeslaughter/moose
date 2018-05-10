#!/usr/bin/env python
import os
import vtk

# Input file and variable
filename = os.path.abspath('mug.e')
nodal_var = 'convected'

# Read Exodus Data
reader0 = vtk.vtkExodusIIReader()
reader0.SetFileName(filename)
reader0.UpdateInformation()
reader0.SetTimeStep(8)
reader0.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
#reader0.Update(); print reader0

reader1 = vtk.vtkExodusIIReader()
reader1.SetFileName(filename)
reader1.UpdateInformation()
reader1.SetTimeStep(9)
reader1.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
#reader1.Update(); print reader1

interp = vtk.vtkInterpolateDataSetAttributes()
interp.AddInputConnection(reader0.GetOutputPort())
interp.AddInputConnection(reader1.GetOutputPort())
interp.SetT(0.5)
#interp.Update(); print interp

# Create Geometry
geometry = vtk.vtkCompositeDataGeometryFilter()
geometry.SetInputConnection(interp.GetOutputPort())
#geometry.SetInputConnection(reader0.GetOutputPort()) # the two readers work alone
#geometry.SetInputConnection(reader1.GetOutputPort())

# Mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(geometry.GetOutputPort())
#mapper.SelectColorArray(nodal_var)
#mapper.SetScalarModeToUsePointFieldData()

# Actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

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
