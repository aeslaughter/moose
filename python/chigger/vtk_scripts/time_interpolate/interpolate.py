#!/usr/bin/env python
import vtk

file0 = 'input_out.e'
file1 = 'input_out.e-s002'
variable = 'u'
range = [0, 10]

# COARSE
reader0 = vtk.vtkExodusIIReader()
reader0.SetFileName(file0)
reader0.UpdateInformation()
reader0.SetTimeStep(0)
reader0.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
reader0.Update()

geometry0 = vtk.vtkCompositeDataGeometryFilter()
geometry0.SetInputConnection(0, reader0.GetOutputPort(0))
geometry0.Update()

mapper0 = vtk.vtkPolyDataMapper()
mapper0.SetInputConnection(geometry0.GetOutputPort())
mapper0.SelectColorArray(variable)
mapper0.SetScalarModeToUsePointFieldData()
mapper0.InterpolateScalarsBeforeMappingOn()
mapper0.SetScalarRange(*range)

actor0 = vtk.vtkActor()
actor0.SetMapper(mapper0)

renderer0 = vtk.vtkRenderer()
renderer0.AddViewProp(actor0)
renderer0.SetViewport(0, 0, 0.5, 1)

# FINE
reader1 = vtk.vtkExodusIIReader()
reader1.SetFileName(file1)
reader1.UpdateInformation()
reader1.SetTimeStep(0)
reader1.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
reader1.Update()

geometry1 = vtk.vtkCompositeDataGeometryFilter()
geometry1.SetInputConnection(0, reader1.GetOutputPort(0))
geometry1.Update()

mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(geometry1.GetOutputPort())
mapper1.SelectColorArray(variable)
mapper1.SetScalarModeToUsePointFieldData()
mapper1.InterpolateScalarsBeforeMappingOn()
mapper1.SetScalarRange(*range)

actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

renderer1 = vtk.vtkRenderer()
renderer1.AddViewProp(actor1)
renderer1.SetViewport(0.5, 0, 1, 1)


# Window and Interactor
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer0)
window.AddRenderer(renderer1)
window.SetSize(1920, 1080)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

window.Render()
interactor.Start()
