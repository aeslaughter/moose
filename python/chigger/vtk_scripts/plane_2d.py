#!/usr/bin/env python
import math
import vtk



source = vtk.vtkPlaneSource()

#p = [0, 0]
source.SetOrigin(0.25, 0.5, 0.)
source.SetPoint1(0.5, 0.25, 0.)
source.SetPoint2(0.5, 0.75, 0.)

#source.SetOrigin(0., 0.5, 0.)
#source.SetPoint1(0.5, 0.0, 0.)
#source.SetPoint2(0.5, 1.0, 0.)

p = source.GetCenter()


# Fills screen
#p = [1, 1]
#source.SetOrigin(-0.5, 0, 0)
#source.SetPoint1(0, -0.5, 0)
#source.SetPoint2(0, 0.5, 0)

#source.SetOrigin(10,10,0)
#source.SetPoint1(490, 10, 0)
#source.SetPoint2(10, 490, 0)

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
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(500, 500)

camera = renderer.MakeCamera()
renderer.SetActiveCamera(camera)

# Coordinate transformation object
tr = vtk.vtkCoordinate()
tr.SetCoordinateSystemToNormalizedViewport()

# Size of window
window_size = renderer.GetRenderWindow().GetSize()
print window_size

# Size of image
bnds = mapper.GetBounds()
size = [bnds[1] - bnds[0], bnds[3] - bnds[2]]
print 'size =', size
###size = mapper.GetBounds()#[1, 1] #source.GetOutput().GetDimensions()


# Normalized image width
#scale = 1#float(window[0])/float(size[0]) * self.getOption('width')
scale = float(window_size[0])/float(size[0]) * size[0]#self.getOption('width')
print 'scale = ', scale

# Compute the camera distance
angle = camera.GetViewAngle()
print 'angle =', angle

#d = window_size[1]*0.5 / math.tan(math.radians(angle*0.5))
d = window_size[1]*0.5 / math.tan(math.radians(angle*0.5))
print 'distance =', d

# Determine the image position
tr.SetValue(p[0], p[1], 0)
position = list(tr.GetComputedDisplayValue(renderer))
print 'position =', position


# Reference position (middle of window)
tr.SetValue(0.5, 0.5, 0)
ref = tr.GetComputedDisplayValue(renderer)

#print ref


# Camera offsets
x = (ref[0] - position[0]) * 1/scale
y = (ref[1] - position[1]) * 1/scale

print 'x = {}; y = {}'.format(x, y)

# Set the camera

camera.SetViewUp(0, 1, 0)
camera.SetPosition(size[0] + x, size[1] + y, d * 1/scale)
#camera.SetFocalPoint(size[0]/2. + x, size[1]/2. + y, 0)
camera.SetFocalPoint(source.GetCenter())
#camera.SetFocalPoint(0,0,0)

print 'pos = ', camera.GetPosition()
print camera, source

# Update the renderer
#renderer.ResetCameraClippingRange()






interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Initialize()

# Show the result
window.Render()
interactor.Start()
print camera
