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
renderer0.SetViewport(0, 0, 0.25, 1)

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
renderer1.SetViewport(0.75, 0, 1, 1)

####################################################################################################
# PROJECT SOLUTION FROM FILE 0 to GRID FROM FILE 1

# Get the data to be interpolated
#source_data = reader0.GetOutput().GetBlock(0).GetBlock(0) # Pc data from file 0 (filter source)

extract = vtk.vtkExtractBlock()
extract.SetInputConnection(reader0.GetOutputPort())
extract.AddIndex(0)
extract.AddIndex(1)
extract.Update()

source_data = extract.GetOutput()



# Build the structure to interpolate on to
output_grid = vtk.vtkUnstructuredGrid() # output to be interpolated on to
#output_grid.DeepCopy(reader1.GetOutput().GetBlock(0).GetBlock(0))
output_grid.CopyStructure(reader1.GetOutput().GetBlock(0).GetBlock(0))

locator = vtk.vtkStaticPointLocator()
locator.SetDataSet(output_grid)
locator.BuildLocator()

#kernel = vtk.vtkLinearKernel()
kernel = vtk.vtkGaussianKernel()
kernel.SetSharpness(4)

interpolator = vtk.vtkPointInterpolator()
interpolator.SetSourceData(source_data) # Pc data set to be probed by input points P
interpolator.SetInputData(output_grid)
interpolator.SetKernel(kernel)
interpolator.SetLocator(locator)
interpolator.SetNullPointsStrategyToClosestPoint()
interpolator.Update()

#geometry2 = vtk.vtkCompositeDataGeometryFilter()
#geometry2.SetInputConnection(0, interpolator.GetOutputPort())
#geometry2.Update()

#mapper2 = vtk.vtkPolyDataMapper()
mapper2 = vtk.vtkDataSetMapper()
mapper2.SetInputConnection(interpolator.GetOutputPort())
mapper2.SelectColorArray(variable)
mapper2.SetScalarModeToUsePointFieldData()
mapper2.InterpolateScalarsBeforeMappingOn()
mapper2.SetScalarRange(*range)

actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)
actor2.GetProperty().SetEdgeVisibility(True)

renderer2 = vtk.vtkRenderer()
renderer2.AddActor(actor2)
renderer2.SetViewport(0.25, 0, 0.5, 1)

# I can't get this to perform interpolation
data = vtk.vtkInterpolateDataSetAttributes()
data.AddInputData(reader1.GetOutput().GetBlock(0).GetBlock(0))
data.AddInputData(interpolator.GetOutput())
data.SetT(0.5)
data.Update()
print data.GetInputList()

print reader1.GetOutput().GetBlock(0).GetBlock(0).GetPointData()
print '-------------------------------------------------------'
print interpolator.GetOutput().GetPointData()
print '-------------------------------------------------------'
print data.GetOutput().GetPointData() # THIS DOESN'T CONTAIN "u"
print data.GetNumberOfInputPorts()

mapper3 = vtk.vtkDataSetMapper()
mapper3.SetInputConnection(data.GetOutputPort())
mapper3.SelectColorArray(variable)
mapper3.SetScalarModeToUsePointFieldData()
mapper3.InterpolateScalarsBeforeMappingOn()
mapper3.SetScalarRange(*range)

actor3 = vtk.vtkActor()
actor3.SetMapper(mapper3)
actor3.GetProperty().SetEdgeVisibility(True)

renderer3 = vtk.vtkRenderer()
renderer3.AddActor(actor3)
renderer3.SetViewport(0.5, 0, 0.75, 1)


####################################################################################################
# Window and Interactor

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer0)
window.AddRenderer(renderer2)
window.AddRenderer(renderer3)
window.AddRenderer(renderer1)
window.SetSize(1920, 1080)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

window.Render()
interactor.Start()
