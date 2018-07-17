#!/usr/bin/env python
import math
import vtk

source = vtk.vtkPlaneSource()
#mapper = vtk.vtkPolyDataMapper2D()
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(source.GetOutputPort())

#actor = vtk.vtkActor2D()
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1,0,0)

renderer = vtk.vtkRenderer()
renderer.AddViewProp(actor)

# Window and Interactor
vtk_window = vtk.vtkRenderWindow()
vtk_window.AddRenderer(renderer)
vtk_window.SetSize(400, 400)

vtkcamera = renderer.MakeCamera()
renderer.SetActiveCamera(vtkcamera)

origin = [0.5, 0.75, 0]
p1 = [0.75, 0.5, 0]
p2 = [0.75, 1, 0]

# Coordinate transformation object
tr = vtk.vtkCoordinate()
tr.SetCoordinateSystemToNormalizedViewport()

window = renderer.GetRenderWindow().GetSize()

#source.SetOrigin(origin[0]*window[0], origin[1]*window[1], 0)
#source.SetPoint1(p1[0]*window[0], p1[1]*window[1], 0)
#source.SetPoint2(p2[0]*window[0], p2[1]*window[1], 0)
source.SetOrigin(origin[0], origin[1], 0)
source.SetPoint1(p1[0], p1[1], 0)
source.SetPoint2(p2[0], p2[1], 0)


p = source.GetOrigin()#[0.5, 0.75]
w = 0.5


# Size of window

# Size of image
bnds = mapper.GetBounds()
size = [bnds[1] - bnds[0], bnds[3] - bnds[2]]
#w = float(size[0])/float(window[0])
#size = self._sources[-1].getVTKSource().GetOutput().GetDimensions()

# Normalized image width
scale = float(window[0])/float(size[0]) * w

# Compute the camera distance
angle = vtkcamera.GetViewAngle()
d = window[1]*0.5 / math.tan(math.radians(angle*0.5))
print size, d, scale

# Determine the image position
tr.SetValue(p[0], p[1], 0)
position = list(tr.GetComputedDisplayValue(renderer))

# Adjust for off-center alignments
#if self.getOption('horizontal_alignment') == 'left':
position[0] = position[0] + (size[0]*0.5*scale)
#elif self.getOption('horizontal_alignment') == 'right':
#    position[0] = position[0] - (size[0]*0.5*scale)
#
#if self.getOption('vertical_alignment') == 'top':
#position[1] = position[1] - (size[1]*0.5*scale)
#elif self.getOption('vertical_alignment') == 'bottom':
position[1] = position[1] + (size[1]*0.5*scale)

# Reference position (middle of window)
tr.SetValue(0.5, 0.5, 0)
ref = tr.GetComputedDisplayValue(renderer)

# Camera offsets
x = (ref[0] - position[0]) * 1/scale
y = (ref[1] - position[1]) * 1/scale

# Set the camera
vtkcamera.SetViewUp(0, 1, 0)
vtkcamera.SetPosition(size[0]/2. + x, size[1]/2. + y, d * 1/scale)
vtkcamera.SetFocalPoint(size[0]/2. + x, size[1]/2. + y, 0)

# Update the renderer
renderer.ResetCameraClippingRange()





interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(vtk_window)
interactor.Initialize()

# Show the result
vtk_window.Render()
interactor.Start()
#print camera
