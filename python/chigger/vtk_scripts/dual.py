#!/usr/bin/env python
#
# This example was built using Python2.7 and VTK6.3 on OSX
import vtk

# Input file and variable
filename = '../tests/input/mug_blocks_out.e'
nodal_var = 'convected'

def add_renderer(window, var, view):
    # Read Exodus Data
    reader = vtk.vtkExodusIIReader()
    reader.SetFileName(filename)
    reader.UpdateInformation()
    reader.SetTimeStep(10)
    reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)  # enables all NODAL variables
    reader.Update()
    # print reader # uncomment this to show the file information

    # Create Geometry
    geometry = vtk.vtkCompositeDataGeometryFilter()
    geometry.SetInputConnection(0, reader.GetOutputPort(0))
    geometry.Update()

    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(geometry.GetOutputPort())
    mapper.SelectColorArray(var)
    mapper.SetScalarModeToUsePointFieldData()
    mapper.InterpolateScalarsBeforeMappingOn()

    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetViewport(view)

    window.AddRenderer(renderer)

    return renderer

# Window and Interactor
window = vtk.vtkRenderWindow()
window.SetSize(600, 600)

r0 = add_renderer(window, 'convected', [0,0,0.5,1])
r1 = add_renderer(window, 'diffused', [0.5,0,1,1])


interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()
interactor.GetInteractorStyle().SetCurrentRenderer(r0)

# Show the result
window.Render()
interactor.Start()
