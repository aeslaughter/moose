#!/usr/bin/env python
import vtk
import mooseutils
import chigger

import logging


from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import base


#@chiggerOutputType("vtkMultiBlockDataSet")
#@chigger.base.InputType("vtkMultiBlockDataSet")
#@base.ChiggerAlgorithm.nInputPorts(1)
#@base.ChiggerAlgorithm.inputType('vtkMultiBlockDataSet')

#@base.ChiggerResult.addFilter('geometry', chigger.filters.GeometryFilter, required=True)
#class ExodusResult(base.ChiggerResult):


#    VTKACTORTYPE = vtk.vtkActor
#    VTKMAPPERTYPE = vtk.vtkPolyDataMapper
#    INPUTTYPE = 'vtkMultiBlockDataSet'


    #def initialize(self):
        #self._setActorType(vtk.vtkPolyDataMapper)

    #    self.__VTKACTORTYPE__ = vtk.vtkPolyDataMapper
    #    self.__VTKMAPPERTYPE__ = vtk.vtkActor
    #    self.__INPUTTYPE__ = 'vtkMultiBlockDataSet'






if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger()


    variable = 'u'
    rng = [0, 14]
    filename = '../input/input_no_adapt_out.e'
    reader = chigger.exodus.ExodusReader(filename, time=2)


   # print reader.GetOutputDataObject(0)

    #print 'call setOptions'
    #reader.setOptions(time=2)

    result = chigger.exodus.ExodusResult(reader)


    """
    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(geometry.GetOutputPort())
    mapper.SelectColorArray(variable)
    mapper.SetScalarRange(*rng)
    mapper.SetScalarModeToUsePointFieldData()
    mapper.InterpolateScalarsBeforeMappingOn()

    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddViewProp(actor)
    """



    # Window and Interactor
    window = vtk.vtkRenderWindow()
    window.AddRenderer(result.getVTKRenderer())
    window.SetSize(600, 600)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.Initialize()

    ## Show the result
    window.Render()
    interactor.Start()
