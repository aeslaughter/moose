#!/usr/bin/env python2
#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
import chigger
text = chigger.annotations.TextAnnotation(text='This is a test.')#, font_size=32,
#                                          text_color=(1.,0.,1.), text_opacity=0.5, layer=0)
text.update()
#text[0].getVTKMapper().SetInput("Testing...")
text[0].getVTKActor().SetMapper(text[0].getVTKMapper())
text.getVTKRenderer().AddActor(text[0].getVTKActor())

#text.initialize()

renWin = vtk.vtkRenderWindow()
renWin.SetSize(1000, 1000)
renWin.AddRenderer(text.getVTKRenderer())

# Create a render window interactor.
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Enable user interface interactor.
iren.Initialize()
renWin.Render()
iren.Start()


#window = chigger.RenderWindow(text, size=(1000,1000), test=False)
#window.update()
#window.write('text_annotation.png')

#window.getVTKInteractor().GetInteractorStyle().SetDefaultRenderer(text.getVTKRenderer())
#window.getVTKInteractor().GetInteractorStyle().SetRenderer(text.getVTKRenderer())

#window.start()
