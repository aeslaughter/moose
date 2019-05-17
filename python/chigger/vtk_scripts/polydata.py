#!/usr/bin/env python
import vtk

name = 'data'

# Define points
points = vtk.vtkPoints()
points.InsertNextPoint(.25, .25, 0)
points.InsertNextPoint(.5, .25, 0)
points.InsertNextPoint(.5, .5, 0)
points.InsertNextPoint(.25, .5, 0)
points.InsertNextPoint(.5, .75, 0)
points.InsertNextPoint(.25, .75, 0)

# Define two quads, one above the other
quad = vtk.vtkQuad()
quad.GetPointIds().SetId(0, 0)
quad.GetPointIds().SetId(1, 1)
quad.GetPointIds().SetId(2, 2)
quad.GetPointIds().SetId(3, 3)

quad2 = vtk.vtkQuad()
quad2.GetPointIds().SetId(0, 3)
quad2.GetPointIds().SetId(1, 2)
quad2.GetPointIds().SetId(2, 4)
quad2.GetPointIds().SetId(3, 5)

cells = vtk.vtkCellArray()
cells.InsertNextCell(quad)
cells.InsertNextCell(quad2)

poly = vtk.vtkPolyData()
poly.SetPoints(points)
poly.SetPolys(cells)

# Populate the cell data
data = vtk.vtkFloatArray()
data.SetName(name)
data.SetNumberOfTuples(2)
for i in xrange(2):
    data.SetValue(i, i)
poly.GetCellData().AddArray(data)

coordinate = vtk.vtkCoordinate()
coordinate.SetCoordinateSystemToNormalizedDisplay()

mapper = vtk.vtkPolyDataMapper2D()
mapper.SetInputData(poly)
mapper.SetScalarModeToUseCellFieldData()
mapper.SetScalarRange(data.GetRange(0))
mapper.SetTransformCoordinate(coordinate)
mapper.ColorByArrayComponent(name, 0)

actor = vtk.vtkActor2D()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor2D(actor)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(window)
iren.Start()
