#!/usr/bin/env python
"""
Script to demonstrate toggling interaction between two actors on one renderer.
"""
import vtk

class Chigger2DInteractorStyle(vtk.vtkInteractorStyleUser):
    ZOOM_FACTOR = 2

    def __init__(self, source):
        self.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.onMouseWheelForward)
        self.AddObserver(vtk.vtkCommand.MouseWheelBackwardEvent, self.onMouseWheelBackward)

        super(Chigger2DInteractorStyle, self).__init__()

        self._source = source

    def onMouseWheelForward(self, obj, event):
        self.zoom(self.ZOOM_FACTOR)
        obj.GetInteractor().GetRenderWindow().Render()

    def onMouseWheelBackward(self, obj, event):
        self.zoom(-self.ZOOM_FACTOR)
        obj.GetInteractor().GetRenderWindow().Render()


    def zoom(self, value):

        origin = self._source.GetOrigin()
        self._source.SetOrigin([origin[0] + value, origin[1] + value, 0])

        p = self._source.GetPoint1()
        self._source.SetPoint1([p[0] + value, p[1] - value, 0])

        p = self._source.GetPoint2()
        self._source.SetPoint2([p[0] - value, p[1] + value, 0])


source1 = vtk.vtkPlaneSource()
source1.SetOrigin([100, 100, 0])
source1.SetPoint1([100, 300, 0])
source1.SetPoint2([300, 100, 0])

mapper1 = vtk.vtkPolyDataMapper2D()
mapper1.SetInputConnection(source1.GetOutputPort())

actor1 = vtk.vtkActor2D()
actor1.SetMapper(mapper1)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor1)

window = vtk.vtkRenderWindow()
window.SetSize(600, 600)
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

style = Chigger2DInteractorStyle(source1)
interactor.SetInteractorStyle(style)
interactor.Initialize()





window.Render()
interactor.Start()
