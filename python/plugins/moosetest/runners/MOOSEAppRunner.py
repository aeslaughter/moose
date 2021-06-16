import os
import subprocess

from moosetools.parameters import InputParameters
from moosetools.moosetest import runners
from moosetools.mooseutils import find_moose_executable_recursive

from ..controllers import MOOSEConfigController, PETScConfigController, LibMeshConfigController

class MOOSEAppRunner(runners.RunCommand):

    @staticmethod
    def validParams():
        params = runners.RunCommand.validParams()
        params.setRequired('command', False) # to be set within the `execute` method

        #params.add('executable', vtype=str, doc="The executable to run, by default this is located automatically.")


        params.add('input', vtype=str, required=True,
                   doc="The input file (*.i) to utilize for running application. The file should be defined relative to the HIT test specification or the current working directory if the object is not being instantiated with a test specification.")
        params.add('cli_args', vtype=str, array=True,
                   doc="Additional command line arguments to pass to the MOOSE application execution.")
        params.add('jacobian', vtype=str, allow=('TEST', 'TEST_AND_RUN'),
                   doc="Enable PETSc options for testing the Jacobian ('TEST') without running the simulation or with running the simulation ('TEST_AND_RUN').")

        params.add('allow_warnings', vtype=bool, default=True,
                   doc="When False the '--error' flag is passed to the executable.")


        # TODO: Remove legacy parameters
        #
        # Appends the listed parameters from each Controller object to parameters on this object,
        # which eliminates the prefix.
        #
        # In the future, this syntax should be removed and the prefix versions used
        params.append(MOOSEConfigController.validObjectParams(), 'ad_mode', 'ad_indexing_type', 'ad_size')
        params.append(PETScConfigController.validObjectParams(), 'superlu', 'mumps', 'strumpack', 'parmetis', 'chaco', 'party', 'ptscotch')
        params.append(LibMeshConfigController.validObjectParams(), 'mesh_mode', 'dof_id_bytes', 'unique_id', 'dtk', 'boost', 'vtk', 'tecplot', 'curl', 'fparser_jit', 'threads', 'tbb', 'openmp')

        # TODO
        params.add('scale_refine')
        params.add('prereq')
        params.add('recover')

        # TODO: Create SQAController
        params.add('design')
        params.add('requirement')
        params.add('issues')
        params.add('detail')

        return params

    def __init__(self, *args, **kwargs):
        runners.RunCommand.__init__(self, *args, **kwargs)

        # TODO: Remove legacy parameters
        #
        # The Controllers system in moosetools.moosetest creates sub-parameters with prefixes. The
        # following takes parameters from this object (see validParams) and sets the correct value
        # in the included Controller objects

        # MOOSE
        self.parameters().setValue('moose_ad_mode', self.getParam('ad_mode'))
        self.parameters().setValue('moose_ad_indexing_type', self.getParam('ad_indexing_type'))
        self.parameters().setValue('moose_ad_size', self.getParam('ad_size'))

        # PETSc
        self.parameters().setValue('petsc_superlu', self.getParam('superlu'))
        self.parameters().setValue('petsc_mumps', self.getParam('mumps'))
        self.parameters().setValue('petsc_strumpack', self.getParam('strumpack'))
        self.parameters().setValue('petsc_parmetis', self.getParam('parmetis'))
        self.parameters().setValue('petsc_chaco', self.getParam('chaco'))
        self.parameters().setValue('petsc_party', self.getParam('party'))
        self.parameters().setValue('petsc_ptscotch', self.getParam('ptscotch'))

        # libMesh
        self.parameters().setValue('libmesh_mesh_mode', self.getParam('mesh_mode'))
        self.parameters().setValue('libmesh_dof_id_bytes', self.getParam('dof_id_bytes'))
        self.parameters().setValue('libmesh_unique_id', self.getParam('unique_id'))
        self.parameters().setValue('libmesh_dtk', self.getParam('dtk'))
        self.parameters().setValue('libmesh_boost', self.getParam('boost'))
        self.parameters().setValue('libmesh_vtk', self.getParam('vtk'))
        self.parameters().setValue('libmesh_tecplot', self.getParam('tecplot'))
        self.parameters().setValue('libmesh_curl', self.getParam('curl'))
        #self.parameters().setValue('libmesh_slepc', self.getParam('slepc'))
        self.parameters().setValue('libmesh_fparser_jit', self.getParam('fparser_jit'))
        self.parameters().setValue('libmesh_threads', self.getParam('threads'))
        self.parameters().setValue('libmesh_tbb', self.getParam('tbb'))
        self.parameters().setValue('libmesh_openmp', self.getParam('openmp'))

    def execute(self):
        """
        Run MOOSE-based application.
        """

        # Command list to supply base RunCommand
        command = list()

        # Determine working location
        base_dir = self.getFileBase()

        # Locate MOOSE application executable
        exe = find_moose_executable_recursive(base_dir)
        if exe is None:
            self.critical("Unable to locate MOOSE application executable starting in '{}'.", os.getcwd())
            return 1
        command.append(exe)

        # Locate application input file
        input_file = os.path.abspath(os.path.join(base_dir, self.getParam('input')))
        if not os.path.isfile(input_file):
            self.critical("The supplied input file '{}' does not exist in the directory '{}.", self.getParam('input'), base_dir)
            return 1
        command += ['-i', input_file]

        # Append "cli_args" parameters
        command += self.getParam('cli_args') or []

        # Append PETSc Jacobian options
        jac = self.getParam('jacobian')
        if jac == 'TEST' or jac == 'TEST_AND_RUN':
            command += ['-snes_test_jacobian', '-snes_force_iteration']
        if jac == 'TEST_AND_RUN':
            command += ['-snes_type', 'ksponly', '-ksp_type', 'preonly', '-pc_type', 'none', '-snes_convergence_test', 'skip']

        # Error flags
        if not self.getParam('allow_warnings'):
            command.append('--error')

        self.parameters().setValue('command', tuple(command))
        return runners.RunCommand.execute(self)

    def getFileBase(self):
        """
        Determine the base directory for defining relative filenames.
        """
        if '_hit_filename' not in self.parameters():
            base_dir = os.getcwd()
            msg = "The `MOOSEAppRunner` with name '{}' was not created via a HIT file, as such the base directory for files/paths needed to execute the object are not known. The current working directory of '{}' is being used."
            self.warning(msg, self.name(), base_dir)
        else:
            hit_file = self.getParam('_hit_filename')
            base_dir = os.path.dirname(hit_file)
        return base_dir
