#!/usr/bin/env python
import vtk

file0 = 'input_out.e'
file1 = 'input_out.e-s002'
variable = 'u'
range = [0, 10]

##################################################################################
# FILE 0: COARSE MESH WITH SOLUTION 0

coarseReader = vtk.vtkExodusIIReader()
coarseReader.SetFileName(file0)
coarseReader.UpdateInformation()
coarseReader.SetTimeStep(0)
coarseReader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
coarseReader.Update()

coarseGeometry = vtk.vtkCompositeDataGeometryFilter()
coarseGeometry.SetInputConnection(0, coarseReader.GetOutputPort(0))
coarseGeometry.Update()

coarseMapper = vtk.vtkPolyDataMapper()
coarseMapper.SetInputConnection(coarseGeometry.GetOutputPort())
coarseMapper.SelectColorArray(variable)
coarseMapper.SetScalarModeToUsePointFieldData()
coarseMapper.InterpolateScalarsBeforeMappingOn()
coarseMapper.SetScalarRange(*range)

coarseActor = vtk.vtkActor()
coarseActor.SetMapper(coarseMapper)
coarseActor.GetProperty().SetEdgeVisibility(True)

coarseRenderer = vtk.vtkRenderer()
coarseRenderer.AddViewProp(coarseActor)
coarseRenderer.SetViewport(0, 0, 0.25, 1)

####################################################################################################
# FILE 1: FINE MESH WITH SOLUTION 1

fineReader = vtk.vtkExodusIIReader()
fineReader.SetFileName(file1)
fineReader.UpdateInformation()
fineReader.SetTimeStep(0)
fineReader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
fineReader.Update()

fineGeometry = vtk.vtkCompositeDataGeometryFilter()
fineGeometry.SetInputConnection(0, fineReader.GetOutputPort(0))
fineGeometry.Update()

fineGeometry.GetOutput().GetPointData().SetActiveScalars(variable)


fineMapper = vtk.vtkPolyDataMapper()
fineMapper.SetInputConnection(fineGeometry.GetOutputPort())
fineMapper.SelectColorArray(variable)
fineMapper.SetScalarModeToUsePointFieldData()
fineMapper.InterpolateScalarsBeforeMappingOn()
fineMapper.SetScalarRange(*range)

fineActor = vtk.vtkActor()
fineActor.SetMapper(fineMapper)
fineActor.GetProperty().SetEdgeVisibility(True)

fineRenderer = vtk.vtkRenderer()
fineRenderer.AddViewProp(fineActor)
fineRenderer.SetViewport(0.75, 0, 1, 1)

####################################################################################################
# PROJECT SOLUTION FROM FILE 0 to GRID FROM FILE 1

# Build the structure to interpolate onto
coarseInterpolatedGrid = vtk.vtkUnstructuredGrid()

coarseMultiBlock = vtk.vtkMultiBlockDataSet.SafeDownCast(coarseReader.GetOutput().GetBlock(0))
coarseInterpolatedGrid.DeepCopy(vtk.vtkUnstructuredGrid.SafeDownCast(coarseMultiBlock.GetBlock(0)))

locator = vtk.vtkStaticPointLocator()
locator.SetDataSet(fineGeometry.GetOutput())
locator.BuildLocator()

kernel = vtk.vtkGaussianKernel()
kernel.SetSharpness(4)
kernel.SetKernelFootprintToNClosest()
kernel.SetNumberOfPoints(10)
kernel.SetSharpness(5.0)

coarseInterpolator = vtk.vtkPointInterpolator()
coarseInterpolator.SetSourceData(fineGeometry.GetOutput()) # Pc data set to be probed by input points P
coarseInterpolator.SetInputData(coarseGeometry.GetOutput())
coarseInterpolator.SetKernel(kernel)
coarseInterpolator.SetLocator(locator)
coarseInterpolator.SetNullPointsStrategyToClosestPoint()
coarseInterpolator.PassPointArraysOff()
coarseInterpolator.Update()

coarseInterpolatorMapper = vtk.vtkDataSetMapper()
coarseInterpolatorMapper.SetInputConnection(coarseInterpolator.GetOutputPort())
coarseInterpolatorMapper.SelectColorArray(variable)
coarseInterpolatorMapper.SetScalarModeToUsePointFieldData()
coarseInterpolatorMapper.InterpolateScalarsBeforeMappingOn()
coarseInterpolatorMapper.SetScalarRange(*range)

coarseInterpolatorActor = vtk.vtkActor()
coarseInterpolatorActor.SetMapper(coarseInterpolatorMapper)
coarseInterpolatorActor.GetProperty().SetEdgeVisibility(True)

coarseInterpolatorRenderer = vtk.vtkRenderer()
coarseInterpolatorRenderer.AddActor(coarseInterpolatorActor)
coarseInterpolatorRenderer.SetViewport(0.25, 0, 0.5, 1)

# I can't get this to perform interpolation
coarseInterpolatedGrid.GetPointData().SetActiveScalars(variable)
coarseInterpolator.GetOutput().GetPointData().SetActiveScalars(variable)

coarseInterpolateAttributes = vtk.vtkInterpolateDataSetAttributes()
coarseInterpolateAttributes.AddInputData(0, coarseInterpolatedGrid)
coarseInterpolateAttributes.AddInputData(0, coarseInterpolator.GetOutput())
coarseInterpolateAttributes.SetT(0.5)
coarseInterpolateAttributes.Update()

coarseInterpolateAttibutesMapper = vtk.vtkDataSetMapper()
coarseInterpolateAttibutesMapper.SetInputConnection(coarseInterpolateAttributes.GetOutputPort())
coarseInterpolateAttibutesMapper.SelectColorArray(variable)
coarseInterpolateAttibutesMapper.SetScalarModeToUsePointFieldData()
coarseInterpolateAttibutesMapper.InterpolateScalarsBeforeMappingOn()
coarseInterpolateAttibutesMapper.SetScalarRange(*range)

coarseInterpolateAttibutesActor = vtk.vtkActor()
coarseInterpolateAttibutesActor.SetMapper(coarseInterpolateAttibutesMapper)
coarseInterpolateAttibutesActor.GetProperty().SetEdgeVisibility(True)

coarseInterpolateAttibutesMapperRenderer = vtk.vtkRenderer()
coarseInterpolateAttibutesMapperRenderer.AddActor(coarseInterpolateAttibutesActor)
coarseInterpolateAttibutesMapperRenderer.SetViewport(0.5, 0, 0.75, 1)


####################################################################################################
# Window and Interactor

window = vtk.vtkRenderWindow()
window.AddRenderer(fineRenderer)
window.AddRenderer(coarseInterpolatorRenderer)
window.AddRenderer(coarseInterpolateAttibutesMapperRenderer)
window.AddRenderer(coarseRenderer)
window.SetSize(1920, 1080)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

window.Render()
interactor.Start()
