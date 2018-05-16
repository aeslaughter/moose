#!/usr/bin/env python
import os
import vtk

from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

"""
class TimeSeries(object):

    def Initialize(self, vtkself):
        vtkself.SetNumberOfInputPorts(1)
        vtkself.SetNumberOfOutputPorts(1)

    def ProcessRequest(self, vtkself, request, inInfo, outInfo):

        if request.Has(vtk.vtkDemandDrivenPipeline.REQUEST_


        elif request.Has(vtk.vtkDemandDrivenPipeline.REQUEST_DATA()):
            inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
            out = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
            out.ShallowCopy(inp)

        #elif request.Has(vtk.vtkDemandDrivenPipeline.REQUEST_UPDATE_TIME()):
         #   print request
        #else:
        #    print '\n'.join(dir(request))
            #info = outInfo.GetInformationObject(0)
            #t = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_TIME_STEP())
            #info.Set(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_TIME_STEP(), 0.55)

        return 1

    def FillInputPortInformation(self, vtkself, port, info):
        info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkMultiBlockDataSet")
        return 1

    def FillOutputPortInformation(self, vtkself, port, info):
        info.Set(vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkMultiBlockDataSet")
        return 1
"""

class TimeSeries(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkMultiBlockDataSet',
                                        nOutputPorts=1, outputType='vtkMultiBlockDataSet')


    def RequestData(self, request, inInfo, outInfo):
        data_in = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        data_out = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        data_out.ShallowCopy(data_in)
        return 1


# Input file and variable
filename = os.path.abspath('mug.e')
nodal_var = 'convected'

# Read Exodus Data
reader = vtk.vtkExodusIIReader()
reader.SetFileName(filename)
reader.UpdateInformation()
reader.SetTimeStep(10)
reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
reader.Update();

#series = vtk.vtkPythonAlgorithm()
#series.SetPythonObject(TimeSeries())
series = TimeSeries()
series.SetInputConnection(reader.GetOutputPort())

# Time interpolation (How do I set this up?)
#time = vtk.vtkTemporalInterpolator()
#time.SetInputConnection(series.GetOutputPort())
#time.SetResampleFactor(2)
#time.Update()



# Create Geometry
geometry = vtk.vtkCompositeDataGeometryFilter()
geometry.SetInputConnection(series.GetOutputPort())
geometry.Update()

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
