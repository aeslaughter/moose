#!/usr/bin/env python
import vtk

file0 = 'input_out.e'
file1 = 'input_out.e-s002'
variable = 'u'
range = [0, 10]

##################################################################################
# FILE 0: COARSE MESH WITH SOLUTION 0
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
actor0.GetProperty().SetEdgeVisibility(True)

renderer0 = vtk.vtkRenderer()
renderer0.AddViewProp(actor0)
renderer0.SetViewport(0, 0, 0.33, 1)

####################################################################################################
# FILE 1: FINE MESH WITH SOLUTION 1

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
actor1.GetProperty().SetEdgeVisibility(True)

renderer1 = vtk.vtkRenderer()
renderer1.AddViewProp(actor1)
renderer1.SetViewport(0.66, 0, 1, 1)

####################################################################################################
# PROJECT SOLUTION FROM FILE 0 to GRID FROM FILE 1

# Get the data to be interpolated
source_data = reader0.GetOutput().GetBlock(0).GetBlock(0) # Pc data from file 0 (filter source)
print source_data.GetPointData() # this is the data I want to interpolate

# Build the structure to interpolate on to (this doesn't seem to work)
output_grid = vtk.vtkUnstructuredGrid() # output P to te interpolated on to
reader1.GetOutput().GetBlock(0).GetBlock(0).DeepCopy(output_grid)
print output_grid.GetPointData()

locator = vtk.vtkStaticPointLocator()
locator.SetDataSet(source_data)
locator.BuildLocator()

kernel = vtk.vtkLineKernel()

interpolator = vtk.vtkPointInterpolator()
interpolator.SetSourceData(source_data) # Pc data set to be probed by input points P
interpolator.SetInputData(output_grid)
interpolator.SetKernel(kernel)
interpolator.SetLocator(locator)
interpolator.SetNullPointsStrategyToClosestPoint()
interpolator.Update()

geometry2 = vtk.vtkCompositeDataGeometryFilter()
geometry2.SetInputConnection(0, interpolator.GetOutputPort())
geometry2.Update()

mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInputConnection(geometry2.GetOutputPort())
mapper2.SelectColorArray(variable)
mapper2.SetScalarModeToUsePointFieldData()
mapper2.InterpolateScalarsBeforeMappingOn()
mapper2.SetScalarRange(*range)

actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)

renderer2 = vtk.vtkRenderer()
renderer2.AddActor(actor2)
renderer2.SetViewport(0.33, 0, 0.66, 1)

####################################################################################################
# Window and Interactor

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer0)
window.AddRenderer(renderer2)
window.AddRenderer(renderer1)
window.SetSize(1920, 1080)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

window.Render()
interactor.Start()
