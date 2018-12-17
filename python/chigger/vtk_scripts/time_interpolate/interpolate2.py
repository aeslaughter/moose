#!/usr/bin/env python
import vtk

file0 = 'input_out.e'
file1 = 'input_out.e-s002'
variable = 'cell'
range = [0, 3]

##################################################################################
# FILE 0: COARSE MESH WITH SOLUTION 0

coarseReader = vtk.vtkExodusIIReader()
coarseReader.SetFileName(file0)
coarseReader.UpdateInformation()
coarseReader.SetTimeStep(0)
coarseReader.SetPointResultArrayStatus(variable, 1)
coarseReader.SetElementResultArrayStatus(variable, 1)
coarseReader.SetGlobalResultArrayStatus(variable, 1)
coarseReader.Update()

coarseGeometry = vtk.vtkCompositeDataGeometryFilter()
coarseGeometry.SetInputConnection(0, coarseReader.GetOutputPort(0))
coarseGeometry.Update()

#coarseGeometry.GetOutput().GetPointData().SetActiveScalars(variable)
#coarseGeometry.GetOutput().GetCellData().SetActiveScalars(variable)

coarseMapper = vtk.vtkPolyDataMapper()
coarseMapper.SetInputConnection(coarseGeometry.GetOutputPort())
coarseMapper.SelectColorArray(variable)

if variable == 'cell':
    coarseMapper.SetScalarModeToUseCellFieldData()
elif variable == 'point':
    coarseMapper.SetScalarModeToUsePointFieldData()


coarseMapper.InterpolateScalarsBeforeMappingOn()
coarseMapper.SetScalarRange(*range)

coarseActor = vtk.vtkActor()
coarseActor.SetMapper(coarseMapper)
coarseActor.GetProperty().SetEdgeVisibility(True)

coarseRenderer = vtk.vtkRenderer()
coarseRenderer.AddViewProp(coarseActor)
coarseRenderer.SetViewport(0, 0, 0.33, 1)

####################################################################################################
# FILE 1: FINE MESH WITH SOLUTION 1

fineReader = vtk.vtkExodusIIReader()
fineReader.SetFileName(file1)
fineReader.UpdateInformation()
fineReader.SetPointResultArrayStatus(variable, 1)
fineReader.SetElementResultArrayStatus(variable, 1)
fineReader.SetGlobalResultArrayStatus(variable, 1)
fineReader.SetGenerateObjectIdCellArray(True)
fineReader.SetTimeStep(0)
fineReader.Update()

fineGeometry = vtk.vtkCompositeDataGeometryFilter()
fineGeometry.SetInputConnection(0, fineReader.GetOutputPort(0))
fineGeometry.Update()

if variable == 'cell':
    fineGeometry.GetOutput().GetCellData().SetActiveScalars(variable)
elif variable == 'point':
    fineGeometry.GetOutput().GetPointData().SetActiveScalars(variable)


fineMapper = vtk.vtkPolyDataMapper()
fineMapper.SetInputConnection(fineGeometry.GetOutputPort())
fineMapper.SelectColorArray(variable)
if variable == 'cell':
    fineMapper.SetScalarModeToUseCellFieldData()
elif variable == 'point':
    fineMapper.SetScalarModeToUsePointFieldData()
fineMapper.InterpolateScalarsBeforeMappingOn()
fineMapper.SetScalarRange(*range)

fineActor = vtk.vtkActor()
fineActor.SetMapper(fineMapper)
fineActor.GetProperty().SetEdgeVisibility(True)

fineRenderer = vtk.vtkRenderer()
fineRenderer.AddViewProp(fineActor)
fineRenderer.SetViewport(0.66, 0, 1, 1)

####################################################################################################
# PROJECT SOLUTION FROM FILE 0 to GRID FROM FILE 1

interpReader = vtk.vtkMultiBlockDataSetAlgorithm()
interpReader.GetOutput().DeepCopy(fineReader.GetOutput())

def interpolate(variable, i, j, action):

    locator = vtk.vtkStaticPointLocator()# switching this to vtkSaticCellLocator doesn't work because vtkPoinInterpolator expects a AbstractPointLocator
    locator.SetDataSet(fineGeometry.GetOutput())
    locator.BuildLocator()

    kernel = vtk.vtkGaussianKernel()
    kernel.SetSharpness(4)
    kernel.SetKernelFootprintToNClosest()
    kernel.SetNumberOfPoints(10)
    kernel.SetSharpness(5.0)

    fineInterpolator = vtk.vtkPointInterpolator()
    fineInterpolator.SetSourceData(coarseGeometry.GetOutput()) # Pc data set to be probed by input points P
    fineInterpolator.SetInputData(fineGeometry.GetOutput())
    fineInterpolator.SetKernel(kernel)
    fineInterpolator.SetLocator(locator)
    fineInterpolator.SetNullPointsStrategyToClosestPoint()

    # THIS IS REQUIRED!!!
    if action == 'CELL':
        fineInterpolator.PassCellArraysOff()
    elif action == 'POINT':
        fineInterpolator.PassPointArraysOff()

    fineInterpolator.Update()

    if action == 'CELL':
        interpReader.GetOutput().GetBlock(i).GetBlock(j).GetCellData().SetActiveScalars(variable)
        fineInterpolator.GetOutput().GetCellData().SetActiveScalars(variable)

    elif action == 'POINT':
        interpReader.GetOutput().GetBlock(i).GetBlock(j).GetPointData().SetActiveScalars(variable)
        fineInterpolator.GetOutput().GetPointData().SetActiveScalars(variable)

    fineInterpolateAttributes = vtk.vtkInterpolateDataSetAttributes()
    fineInterpolateAttributes.AddInputData(0, interpReader.GetOutput().GetBlock(i).GetBlock(j))
    fineInterpolateAttributes.AddInputData(0, fineInterpolator.GetOutput())
    fineInterpolateAttributes.SetT(0.5)
    fineInterpolateAttributes.Update()

    interpReader.GetOutput().GetBlock(i).GetBlock(j).DeepCopy(fineInterpolateAttributes.GetOutput())



for i in xrange(fineReader.GetOutput().GetNumberOfBlocks()):
    for j in xrange(fineReader.GetOutput().GetBlock(i).GetNumberOfBlocks()):
        data = fineReader.GetOutput().GetBlock(i).GetBlock(j)
        if data is None:
            continue

        # POINT
        p_data = fineReader.GetOutput().GetBlock(i).GetBlock(j).GetPointData()
        for k in xrange(p_data.GetNumberOfArrays()):
            name = p_data.GetArray(k).GetName()
            if fineReader.GetPointResultArrayStatus(name):
                interpolate(name, i, j, 'POINT')

        # CELL
        c_data = fineReader.GetOutput().GetBlock(i).GetBlock(j).GetCellData()
        for k in xrange(c_data.GetNumberOfArrays()):
            name = c_data.GetArray(k).GetName()
            if fineReader.GetElementResultArrayStatus(name):
                interpolate(name, i, j, 'CELL')

        # GLOBAL



fineInterpolatorGeometry = vtk.vtkCompositeDataGeometryFilter()
fineInterpolatorGeometry.SetInputData(0, interpReader.GetOutput())
fineInterpolatorGeometry.Update()

fineInterpolateAttibutesMapper = vtk.vtkPolyDataMapper()
fineInterpolateAttibutesMapper.SetInputConnection(fineInterpolatorGeometry.GetOutputPort(0))

fineInterpolateAttibutesMapper.SelectColorArray(variable)
if variable == 'cell':
    fineInterpolateAttibutesMapper.SetScalarModeToUseCellFieldData()
elif variable == 'point':
    fineInterpolateAttibutesMapper.SetScalarModeToUsePointFieldData()

fineInterpolateAttibutesMapper.InterpolateScalarsBeforeMappingOn()
fineInterpolateAttibutesMapper.SetScalarRange(*range)

fineInterpolateAttibutesActor = vtk.vtkActor()
fineInterpolateAttibutesActor.SetMapper(fineInterpolateAttibutesMapper)
fineInterpolateAttibutesActor.GetProperty().SetEdgeVisibility(True)

fineInterpolateAttibutesMapperRenderer = vtk.vtkRenderer()
fineInterpolateAttibutesMapperRenderer.AddActor(fineInterpolateAttibutesActor)
fineInterpolateAttibutesMapperRenderer.SetViewport(0.33, 0, 0.66, 1)




####################################################################################################
# Window and Interactor

window = vtk.vtkRenderWindow()
window.AddRenderer(fineRenderer)
window.AddRenderer(fineInterpolateAttibutesMapperRenderer)
window.AddRenderer(coarseRenderer)
window.SetSize(1920, 1080)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

window.Render()
interactor.Start()
