#!/usr/bin/env python
import os
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from chigger import utils

class ChiggerObject(object):
    """
    Base for all user-facing object in chigger.

    The primary purpose is to provide a method for getting key, value
    options and consistent update methods.
    """

    @staticmethod
    def validOptions():
        """
        Objects should define a static validOptions method to add new key, value options. (public)
        """
        opt = utils.Options()
        #gopt.add('name', vtype=str,
        #g        doc="The object name (this name is displayed on the console help by pressing 'h')."
        #g            "If a name is not supplied the class name is utilized.")
        return opt

    def __init__(self, **kwargs):
        self._options = getattr(self.__class__, 'validOptions')()
        self._options.update(**kwargs)

    def update(self, *args, **kwargs):
        """
        A method for setting/updating an objects options. (public)

        Usage:
           setOptions(sub0, sub1, ..., key0=value0, key1=value1, ...)
           Updates all sub-options with the provided key value pairs

           setOptions(key0=value0, key1=value1, ...)
           Updates the main options with the provided key,value pairs
        """
        # Sub-options case
        if args:
            for sub in args:
                if not self.options().hasOption(sub):
                    msg = "The supplied sub-option '{}' does not exist.".format(sub)
                    mooseutils.mooseError(msg)
                self._options.get(sub).update(**kwargs)

        # Main options case
        else:
            self._options.update(**kwargs)


class ChiggerAlgorithm(ChiggerObject):

    #TODO: check type VTKPythonAlgorithmBase

    def __init__(self, **kwargs):
        ChiggerObject.__init__(self, **kwargs)

        self.Modified()


    def update(self, *args, **kwargs):
        ChiggerObject.update(self, *args, **kwargs)

        for opt in self._options.itervalues():
            if opt.modified > self.GetMTime():
                print opt.name, opt.modified, self.GetMTime()
                self.Modified()


    #def isOptionValid(self, name):
    #    return self._options.isOptionValid(name, self.GetMTime())

    def getOption(self, name):
        return self._options.get(name)



class ExodusReader(VTKPythonAlgorithmBase, ChiggerAlgorithm):
    """I am building a tool for Exodus files, it will be doing all sorts of helpful tasks..."""

    @staticmethod
    def validOptions():
        opt = ChiggerAlgorithm.validOptions()
        #opt.add('time', vtype=float,
        #        doc="The time to view, if not specified the last timestep is displayed.")
        opt.add("timestep", default=-1, vtype=int,
                doc="The simulation timestep. (Use -1 for latest.)")
        #opt.add("adaptive", default=True, vtype=bool,
        #        doc="Load adaptive files (*.e-s* files).")

        return opt

    def __init__(self, filename, **kwargs):
        ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=0, nOutputPorts=1,
                                        outputType='vtkMultiBlockDataSet')

        self.__filename = filename
        self.__active = None

        #for opt in self._options.itervalues():
        #    opt._Option__modified.Modified()


        self.__reader0 = vtk.vtkExodusIIReader()






    def RequestData(self, request, inInfo, outInfo):
        print 'RequestData'

        #self.__reader0.SetFileName(self.__filename)
        #self.__reader0.UpdateInformation()

        self.__reader0.SetTimeStep(self.getOption('timestep'))
        self.__reader0.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1) # enables all NODAL variables
        self.__reader0.Update()

        out_data = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        out_data.ShallowCopy(self.__reader0.GetOutput())
        return 1

    def RequestInformation(self, request, inInfo, outInfo):
        print 'RequestInformation'

        # Create list of filenames to consider
        #filenames = self.__getActiveFilenames()
        #if filenames == self.__active:
        #    return
        #self.__active = filenames



        self.__reader0.SetFileName(self.__filename)
        self.__reader0.UpdateInformation()
        #self.__reader0.SetTimeStep(10)
        return 1


    #def __getActiveFilenames(self):
    #    """
    #    The active ExodusII file(s). (private)

    #    Returns:
    #        list: Contains tuples (filename, modified time) of active file(s).
    #    """
    #    if self.isOptionValid('adaptive'):
    #        return utils.get_active_filenames(self.__filename, self.__filename + '-s*')
    #    else:
    #        return utils.get_active_filenames(self.__filename)




if __name__ == '__main__':
    # Input file and variable
    filename = 'mug_blocks_out.e'
    nodal_var = 'convected'

    reader = ExodusReader(filename, timestep=10)

    # Create Geometry
    geometry = vtk.vtkCompositeDataGeometryFilter()
    geometry.SetInputConnection(0, reader.GetOutputPort(0))

    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(geometry.GetOutputPort())
    mapper.SelectColorArray(nodal_var) # when I used the VTKPytonAlgorithm this doesn't get applied
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
    reader.update(timestep=10)
    window.Render()
    interactor.Start()
