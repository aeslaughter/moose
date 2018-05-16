#!/usr/bin/env python
import os
import vtk
import numpy as np

specifiedTime = 0.18

# Input file and variable
filename = os.path.abspath('mug.e')
nodal_var = 'convected'

# Read Exodus Data
reader = vtk.vtkExodusIIReader()
reader.SetFileName(filename)
reader.UpdateInformation()
reader.SetTimeStep(10)
reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
#reader.Update(); print reader

info = reader.GetExecutive().GetOutputInformation().GetInformationObject(0)
key = vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS()
times = np.array([info.Get(key,i) for i in range(info.Length(key))])
index = np.max(np.where(times <= specifiedTime))

extractTime = vtk.vtkExtractTimeSteps()
extractTime.SetInputConnection(0, reader.GetOutputPort(0))
extractTime.SetTimeStepIndices(2, [index, index+1])

# Time interpolation (How do I set this up?)
time = vtk.vtkTemporalInterpolator()
time.SetInputConnection(0, extractTime.GetOutputPort(0))
time.SetDiscreteTimeStepInterval(specifiedTime - times[index])
time.UpdateTimeStep(specifiedTime)

extractTime2 = vtk.vtkExtractTimeSteps()
extractTime2.SetInputConnection(0, time.GetOutputPort(0))
extractTime2.AddTimeStepIndex(1)

# Create Geometry
geometry = vtk.vtkCompositeDataGeometryFilter()
geometry.SetInputConnection(0, time.GetOutputPort(0))
geometry.Update()

writer = vtk.vtkExodusIIWriter()
writer.SetInputConnection(0, geometry.GetOutputPort())
writer.SetFileName('time.e')
writer.WriteAllTimeStepsOn()
writer.Write()

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
