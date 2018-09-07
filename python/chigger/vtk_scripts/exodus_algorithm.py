#!/usr/bin/env python
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class ExodusReader(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkMultiBlockDataSet',
                                        nOutputPorts=1, outputType='vtkMultiBlockDataSet')


    def RequestData(self, request, inInfo, outInfo):
        if request.Has(vtk.vtkDemandDrivenPipeline.REQUEST_DATA()):
            print 'REQUEST_DATA'

            in_data = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
            out_data = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())

            out_data.ShallowCopy(in_data)
        return 1

    #RequestDataObject(self, request, inInfo, outInfo) : This is where you can create output data objects if the output DATA_TYPE_NAME() is not a concrete type.
    #RequestInformation(self, request, inInfo, outInfo) : Provide meta-data downstream. More on this on later blogs.
    #RequestUpdateExtent(self, request, inInfo, outInfo) : Modify requests coming from downstream. More on this on later blogs.
    #RequestData(self, request, inInfo, outInfo) : Produce data. As described before.

if __name__ == '__main__':
    # Input file and variable
    filename = '../tests/input/mug_blocks_out.e'
    nodal_var = 'convected'

    # Read Exodus Data
    reader = vtk.vtkExodusIIReader()
    reader.SetFileName(filename)
    reader.UpdateInformation()
    reader.SetTimeStep(10)
    reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1) # enables all NODAL variables
    reader.Update()

    my_reader = ExodusReader()
    my_reader.SetInputConnection(reader.GetOutputPort())


    # Create Geometry
    geometry = vtk.vtkCompositeDataGeometryFilter()
    geometry.SetInputConnection(0, my_reader.GetOutputPort(0))
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
