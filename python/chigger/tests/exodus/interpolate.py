#!/usr/bin/env python
import vtk
import mooseutils
import chigger


from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import base



#@chiggerOutputType("vtkMultiBlockDataSet")
#@chigger.base.InputType("vtkMultiBlockDataSet")
class ChiggerResultBase(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):

    # TODO: Set this with decorators
    __VTKACTORTYPE__ = vtk.vtkActor #None
    __VTKMAPPERTYPE__ = vtk.vtkPolyDataMapper #None

    __FILTERS__ = []#
    __REQUIRED_FILTERS__ = []

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()
        return opt

    def __init__(self, *args, **kwargs):
        base.ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1,
                                        inputType='vtkMultiBlockDataSet')#,
                                        #nOutputPorts=1,
                                        #outputType='vtkRenderer')

        renderer = None #TODO: kwargs



        self._geometry = vtk.vtkCompositeDataGeometryFilter()
        self._geometry.SetInputConnection(0, reader.GetOutputPort(0))
        self._geometry.Update()



        self._vtkmapper = self.__VTKMAPPERTYPE__() if self.__VTKMAPPERTYPE__ else None
        if (self._vtkmapper is not None) and not isinstance(self._vtkmapper, vtk.vtkAbstractMapper):
            msg = 'The supplied mapper is a {} but must be a vtk.vtkAbstractMapper type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkmapper).__name__))


        self._vtkmapper.SetInputConnection(self._geometry.GetOutputPort())




        #self._vtkrenderer.SetInteractive(False)


        self._vtkactor = self.__VTKACTORTYPE__() if self.__VTKACTORTYPE__ else None
        if (self._vtkactor is not None) and not isinstance(self._vtkactor, vtk.vtkProp):
            msg = 'The supplied actor is a {} but must be a vtk.vtkProp type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkactor).__name__))


        if self._vtkmapper is not None:
            self._vtkactor.SetMapper(self._vtkmapper)



        self._vtkrenderer = renderer if renderer != None else vtk.vtkRenderer()
        if not isinstance(self._vtkrenderer, vtk.vtkRenderer):
            msg = "The supplied value for the renderer is a {} but it must be of type vtkRenderer."
            raise mooseutils.MooseException(msg.format(type(self._vtkrenderer).__name__))


        if self._vtkactor is not None:
            self._vtkrenderer.AddActor(self._vtkactor)


        #self._vtklight = vtk.vtkLight()
        #self._vtklight.SetLightTypeToHeadlight()


        #self._render_window = None
        #self.__highlight = None

    #def Update(self):
    #    print 'Update"
    def applyOptions(self):
        # TODO: call this automatically ...
        # Can I use the RenderEvent to call this???

        print 'here'


    def RequestInformation(self, request, inInfo, outInfo):

        # TODO: can I create an observer that calls this ???

        print 'REQUEST INFORMATION...'

        return 1

    def RequestData(self, request, inInfo, outInfo):
        print 'REQUEST DATA...'


        out_data = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        print out_data
        out_data.ShallowCopy(self._vtkrenderer)


        return 1

    def getVTKRenderer(self):
        """Return the vtk.vtkRenderer object."""
        return self._vtkrenderer




    def getVTKActor(self):
        """
        Return the constructed vtk actor object. (public)

        Returns:
            An object derived from vtk.vtkProp.
        """
        return self._vtkactor

    def getVTKMapper(self):
        """
        Return the constructed vtk mapper object. (public)

        Returns:
            An object derived from vtk.vtkAbstractMapper
        """
        return self._vtkmapper





if __name__ == '__main__':




    variable = 'u'
    rng = [0, 14]
    filename = '../input/input_no_adapt_out.e'
    reader = chigger.exodus.ExodusReader(filename)


    reader.setOptions(time=2)








    result = ChiggerResultBase(reader)


    print result.updateOptions()


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

    # Show the result
    window.Render()
    interactor.Start()
