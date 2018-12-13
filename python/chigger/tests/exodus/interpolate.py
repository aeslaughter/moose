#!/usr/bin/env python
import vtk
import mooseutils
import chigger

import logging


from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from chigger import base



class ChiggerFilter(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):

    __VTKFILTERTYPE__ = None

    @staticmethod
    def vtkFilterType(vtktype):
        def create(cls):
            cls.__VTKFILTERTYPE__ = vtktype
            return cls
        return create

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()
        opt.add('required', default=False, vtype=bool,
                doc="When set to True this filter will be created automatically.")
        return opt

    def __init__(self, **kwargs):
        base.ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self)

        self.SetNumberOfInputPorts(1)
        self.InputType = 'vtkMultiBlockDataSet'

        self.SetNumberOfOutputPorts(1)
        self.OutputType = 'vtkPolyData'

        self._vtkfilter = self.__VTKFILTERTYPE__()

    def RequestData(self, request, inInfo, outInfo):
        self.log('RequestData')#, level=logging.DEBUG)


        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())


        self._vtkfilter.SetInputData(inp)
        self._vtkfilter.Update()
        opt.ShallowCopy(self._vtkfilter.GetOutput())
        return 1

    def applyOptions(self):
        pass


@ChiggerFilter.vtkFilterType(vtk.vtkCompositeDataGeometryFilter)
class GeometryFilter(ChiggerFilter):
    pass


#@chiggerOutputType("vtkMultiBlockDataSet")
#@chigger.base.InputType("vtkMultiBlockDataSet")
#@base.ChiggerAlgorithm.nInputPorts(1)
#@base.ChiggerAlgorithm.inputType('vtkMultiBlockDataSet')

class ChiggerResult(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):
    # TODO: Handle multiple inputs with multiple ports


    @staticmethod
    def vtkActorType(vtktype):
        def create(cls):
            cls.__VTKACTORTYPE__ = vtktype
            return cls
        return create

    @staticmethod
    def vtkMapperType(vtktype):
        def create(cls):
            cls.__VTKMAPPERTYPE__ = vtktype
            return cls
        return create

    @staticmethod
    def addFilter(name, filtertype, required=False):
        def create(cls):
            cls.__FILTERS__.append((name, filtertype, required))
            return cls
        return create

    __VTKACTORTYPE__ = None#vtk.vtkActor #None
    __VTKMAPPERTYPE__ = None#vtk.vtkPolyDataMapper #None

    __FILTERS__ = list()#[]#('geometry', GeometryFilter, True)]#

    @staticmethod
    def validOptions():
        opt = base.ChiggerAlgorithm.validOptions()

        for filter_name, filter_type, filter_required in ChiggerResult.__FILTERS__:
            opt.add(filter_name, filter_type.validOptions())
            if filter_required:
                opt.get(filter_name).set('required', True)


        return opt

    def __init__(self, *args, **kwargs):
        base.ChiggerAlgorithm.__init__(self,
        #                               nInputPorts=1,
        #                               inputType='vtkMultiBlockDataSet',
                                       **kwargs)
        VTKPythonAlgorithmBase.__init__(self)
        #  VTKPythonAlgorithmBase.__init__(self,
        #                                  nInputPorts=1,
        #                                  inputType='vtkMultiBlockDataSet')#,
        #                                  #nOutputPorts=1,
        #                                  #outputType='vtkRenderer')

        self.SetNumberOfInputPorts(len(args))
        self.InputType = 'vtkMultiBlockDataSet'


        renderer = None #TODO: kwargs

        self._filters = []



        connected = False
        for filter_name,filter_type, filter_required in self.__FILTERS__:

            if not filter_required:
                continue

            self._filters.append(filter_type())

            if not connected:
                self._filters[-1].SetInputConnection(0, args[0].GetOutputPort(0))
                connected = True

            else:
                self._filters[-1].SetInputConnection(0, self._filters[-2].GetOutputPort(0))


        #self._geometry = vtk.vtkCompositeDataGeometryFilter()
        #self._geometry = GeometryFilter()
        #self._geometry.SetInputConnection(0, reader.GetOutputPort(0))
        #self._geometry.Update()



        self._vtkmapper = self.__VTKMAPPERTYPE__() if self.__VTKMAPPERTYPE__ else None
        if (self._vtkmapper is not None) and not isinstance(self._vtkmapper, vtk.vtkAbstractMapper):
            msg = 'The supplied mapper is a {} but must be a vtk.vtkAbstractMapper type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkmapper).__name__))


        if self._filters:
            self._vtkmapper.SetInputConnection(self._filters[-1].GetOutputPort(0))

        else:
            self._vtkmapper.SetInputConnection(args[0].GetOutputPort(0))


        #self._vtkmapper.SetInputConnection(self._geometry.GetOutputPort())


        self._vtkmapper.SelectColorArray('u')
        self._vtkmapper.SetScalarModeToUsePointFieldData()

        self._vtkmapper.InterpolateScalarsBeforeMappingOn()

        #self._vtkrenderer.SetInteractive(False)


        self._vtkactor = self.__VTKACTORTYPE__() if self.__VTKACTORTYPE__ else None
        if (self._vtkactor is not None) and not isinstance(self._vtkactor, vtk.vtkProp):
            msg = 'The supplied actor is a {} but must be a vtk.vtkProp type.'
            raise mooseutils.MooseException(msg.format(type(self._vtkactor).__name__))


        if self._vtkmapper is not None:
            self._vtkactor.SetMapper(self._vtkmapper)



        self._vtkrenderer = renderer if renderer is not None else vtk.vtkRenderer()
        if not isinstance(self._vtkrenderer, vtk.vtkRenderer):
            msg = "The supplied value for the renderer is a {} but it must be of type vtkRenderer."
            raise mooseutils.MooseException(msg.format(type(self._vtkrenderer).__name__))


        if self._vtkactor is not None:
            self._vtkrenderer.AddActor(self._vtkactor)


        #self._vtklight = vtk.vtkLight()
        #self._vtklight.SetLightTypeToHeadlight()


        #self._render_window = None
        #self.__highlight = None

    def applyOptions(self):
        """
        """
        pass


    def RequestInformation(self, request, inInfo, outInfo):
        raise NotImplementedError;
        return 1

    def RequestData(self, request, inInfo, outInfo):
        raise NotImplementedError;
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

@ChiggerResult.vtkMapperType(vtk.vtkPolyDataMapper)
@ChiggerResult.vtkActorType(vtk.vtkActor)
@ChiggerResult.addFilter('geometry', GeometryFilter, required=True)
class ExodusResult(ChiggerResult):
    pass


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

    result = ExodusResult(reader)


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
