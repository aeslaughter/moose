import os
import re
import subprocess

from moosetools.parameters import InputParameters
from moosetools.moosetest import runners
from moosetools.mooseutils import find_moose_executable_recursive

from ..controllers import MOOSEConfigController, PETScConfigController, LibMeshConfigController

class MOOSEAppRunner(runners.ExecuteCommand):

    @staticmethod
    def validParams():
        params = runners.ExecuteCommand.validParams()
        params.setRequired('command', False) # to be set within the `execute` method

        #params.add('executable', vtype=str, doc="The executable to run, by default this is located automatically.")


        params.add('input', vtype=str, required=True,
                   doc="The input file (*.i) to utilize for running application. The file should be defined relative to the HIT test specification or the current working directory if the object is not being instantiated with a test specification.")
        params.add('cli_args', vtype=str, array=False,
                   doc="Additional command line arguments to pass to the MOOSE application execution.")


        # TODO: I am not sure about this approach yet...perhaps "jacobian_test=True and jacobian_test_and_run=True"
        params.add('jacobian', vtype=str, allow=('TEST', 'TEST_AND_RUN'),
                   doc="Enable PETSc options for testing the Jacobian ('TEST') without running the simulation or with running the simulation ('TEST_AND_RUN').")

        # Command-line flags
        params.add('allow_warnings', vtype=bool, default=True,
                   doc="When False the '--error' flag is passed to the executable.")
        params.add('allow_unused', vtype=bool, default=True,
                   doc="When False the '--error-unused' flag is passed to the executable.")
        params.add('allow_override', vtype=bool, default=True,
                   doc="When False the '--override' flag is passed to the executable.")
        params.add('allow_deprecated', vtype=bool, default=True,
                   doc="When False the '--deprecated' flag is passed to the executable.")
        params.add('allow_test_objects', vtype=bool, default=False,
                   doc="Allow the use of test objects by adding '--allow-test-objects' to the MOOSE application command.")

        # Threading parameters
        thread = InputParameters()
        thread.add('count', vtype=int,
                   doc="Set the number of threads to specific value for running application.")
        thread.add('max', vtype=int,
                   doc="Maximum number of threads processes to utilize when running application, this will override the value supplied in 'n_processors'.")
        thread.add('min', vtype=int,
                   doc="Minimum number of threads processes to utilize when running application, this will override the value supplied in 'n_processors'.")
        params.add('thread', default=thread, doc="Set thread counts and limits.")

        # MPI parameters
        mpi = InputParameters()
        mpi.add('count', vtype=int,
                doc="Set the number of MPI processors to specific value for running application.")
        mpi.add('max', vtype=int,
                doc="Maximum number of MPI processes to utilize when running application, this will override the value supplied in 'n_processors'.")
        mpi.add('min', vtype=int,
                doc="Minimum number of MPI processes to utilize when running application, this will override the value supplied in 'n_processors'.")
        params.add('mpi', default=mpi, doc="Set MPI processors counts and limits.")


        # TODO: Remove legacy parameters
        #
        # Appends the listed parameters from each Controller object to parameters on this object,
        # which eliminates the prefix.
        #
        # In the future, this syntax should be removed and the prefix versions used
        params.append(MOOSEConfigController.validObjectParams(), 'ad_mode', 'ad_indexing_type', 'ad_size')
        params.append(PETScConfigController.validObjectParams(), 'superlu', 'mumps', 'strumpack', 'parmetis', 'chaco', 'party', 'ptscotch')
        params.append(LibMeshConfigController.validObjectParams(), 'mesh_mode', 'dof_id_bytes', 'unique_id', 'dtk', 'boost', 'vtk', 'tecplot', 'curl', 'fparser_jit', 'threads', 'tbb', 'openmp', 'methods', 'compiler')

        params.add('max_parallel', vtype=int, doc="Replaced by 'mpi_max'.")
        params.add('min_parallel', vtype=int, doc="Replaced by 'mpi_min'.")

        params.add('max_threads', vtype=int, doc="Replaced by 'thread_max'.")
        params.add('min_threads', vtype=int, doc="Replaced by 'thread_min'.")

        params.add('method', vtype=str, array=True, doc="Replaced by 'libmesh_methods'.")

        params.add('prereq', vtype=str, array=True, doc="Replaced by 'requires'.")

        params.add('valgrind', vtype=str, allow=('HEAVY', 'heavy', 'NONE', 'none'),
                   doc="Replaced by 'mem_mode' (see ValgrindController).")

        params.add('skip', vtype=str, doc="Replaced by 'disable_reason'.")
        params.add('deleted', vtype=str, doc="Replaced by 'disable_reason' and 'disable_method'.")

        params.add('delete_output_before_running', vtype=bool, doc="Replace by 'file_clean'.")
        params.add('should_execute', vtype=bool, default=True)

        # TODO
        params.add('scale_refine')
        params.add('recover')
        params.add('group') # is group still used?
        params.add('custom_cmp')
        params.add('timing')

        # TODO: Create SQAController
        params.add('design')
        params.add('requirement')
        params.add('issues')
        params.add('detail')
        params.add('deprecated')

        return params

    def __init__(self, *args, **kwargs):
        runners.ExecuteCommand.__init__(self, *args, **kwargs)

        # TODO: Remove legacy parameters
        #
        # The Controllers system in moosetools.moosetest creates sub-parameters with prefixes. The
        # following takes parameters from this object (see validParams) and sets the correct value
        # in the included Controller objects

        # MOOSE
        self.parameters().setValue('moose', 'ad_mode', self.getParam('ad_mode'))
        self.parameters().setValue('moose', 'ad_indexing_type', self.getParam('ad_indexing_type'))
        self.parameters().setValue('moose', 'ad_size', self.getParam('ad_size'))

        # PETSc
        self.parameters().setValue('petsc', 'superlu', self.getParam('superlu'))
        self.parameters().setValue('petsc', 'mumps', self.getParam('mumps'))
        self.parameters().setValue('petsc', 'strumpack', self.getParam('strumpack'))
        self.parameters().setValue('petsc', 'parmetis', self.getParam('parmetis'))
        self.parameters().setValue('petsc', 'chaco', self.getParam('chaco'))
        self.parameters().setValue('petsc', 'party', self.getParam('party'))
        self.parameters().setValue('petsc', 'ptscotch', self.getParam('ptscotch'))

        # libMesh
        self.parameters().setValue('libmesh', 'mesh_mode', self.getParam('mesh_mode'))
        self.parameters().setValue('libmesh', 'dof_id_bytes', self.getParam('dof_id_bytes'))
        self.parameters().setValue('libmesh', 'unique_id', self.getParam('unique_id'))
        self.parameters().setValue('libmesh', 'dtk', self.getParam('dtk'))
        self.parameters().setValue('libmesh', 'boost', self.getParam('boost'))
        self.parameters().setValue('libmesh', 'vtk', self.getParam('vtk'))
        self.parameters().setValue('libmesh', 'tecplot', self.getParam('tecplot'))
        self.parameters().setValue('libmesh', 'curl', self.getParam('curl'))
        #self.parameters().setValue('libmesh_slepc', self.getParam('slepc'))
        self.parameters().setValue('libmesh', 'fparser_jit', self.getParam('fparser_jit'))
        self.parameters().setValue('libmesh', 'threads', self.getParam('threads'))
        self.parameters().setValue('libmesh', 'tbb', self.getParam('tbb'))
        self.parameters().setValue('libmesh', 'openmp', self.getParam('openmp'))
        self.parameters().setValue('libmesh', 'methods', self.getParam('methods') or tuple())
        self.parameters().setValue('libmesh', 'compiler', self.getParam('compiler') or tuple())

        self.parameters().setValue('requires', self.getParam('prereq') or tuple())

        self.parameters().setValue('mem', 'mode', self.getParam('valgrind'))

        if self.getParam('delete_output_before_running'):
            self.parameters().setValue('file', 'clean', True)
            self.parameters().setValue('file', 'names_created', tuple())
            self.parameters().setValue('file', 'check_created', False)

        reason = self.getParam('skip')
        if reason is not None:
            self.parameters().setValue('disable', 'reason', reason)
            self.parameters().setValue('disable', 'method', 'SKIP')
        reason = self.getParam('deleted')
        if reason is not None:
            self.parameters().setValue('disable', 'reason', reason)
            self.parameters().setValue('disable', 'method', 'REMOVE')

    def execute(self):
        """
        Run MOOSE-based application.
        """

        # TODO: Deprecated parameters
        mpi_max = self.getParam('max_parallel')
        if mpi_max is not None:
            self.parameters().setValue('mpi', 'max', mpi_max)
        mpi_min = self.getParam('min_parallel')
        if mpi_min is not None:
            self.parameters().setValue('mpi', 'min', mpi_min)

        thd_max = self.getParam('max_threads')
        if thd_max is not None:
            self.parameters().setValue('thread', 'max', thd_max)
        thd_min = self.getParam('min_threads')
        if thd_min is not None:
            self.parameters().setValue('thread', 'min', thd_min)

        if not self.getParam('should_execute'):
            self.info("Execution not performed, 'should_exeucte=False'.")
            return 0
        # End deprecated


        # Command list to supply base ExecuteCommand
        command = list(self.getParam('command') or tuple())

        # Locate MOOSE application executable
        exe = find_moose_executable_recursive()
        if exe is None:
            self.critical("Unable to locate MOOSE application executable starting in '{}'.", os.getcwd())
            return 1
        command.append(exe)

        # Locate application input file
        input_file = self.getParam('input').strip()
        if not os.path.isfile(input_file):
            self.critical("The supplied input file '{}' does not exist.", self.getParam('input'))
            return 1
        command += ['-i', input_file]

        # Append "cli_args" parameters, using a regex that handles spaces with quotes
        if self.isParamValid('cli_args'):
            for match in re.finditer(r"([^\s]*[\"'][^\"']+[\"'][^\s]*)|\S+", self.getParam('cli_args')):
                command.append(match.group(0))

        # Append PETSc Jacobian options
        jac = self.getParam('jacobian')
        if jac == 'TEST' or jac == 'TEST_AND_RUN':
            command += ['-snes_test_jacobian', '-snes_force_iteration']
        if jac == 'TEST_AND_RUN':
            command += ['-snes_type', 'ksponly', '-ksp_type', 'preonly', '-pc_type', 'none', '-snes_convergence_test', 'skip']

        # Error/warning flags
        if not self.getParam('allow_warnings'):
            command.append('--error')
        if not self.getParam('allow_unused'):
            command.append('--error-unused')
        if not self.getParam('allow_override'):
            command.append('--error-override')
        if not self.getParam('allow_deprecated'):
            command.append('--error-deprecated')

        # Test objects
        if self.getParam('allow_test_objects'):
            command += ['--allow-test-objects']

        # MPI
        mpi = self._getParallelCount('mpi')
        if mpi > 1:
            command = ['mpiexec', '-n', str(mpi)] + command

        # Threading
        threads = self._getParallelCount('thread')
        if threads > 1:
            command += ['--n-threads={}'.format(str(threads))]

        self.parameters().setValue('command', tuple(c.strip() for c in command))
        return runners.ExecuteCommand.execute(self)

    def _getParallelCount(self, prefix):
        """
        Return the desired number of processors for the given *prefix*, which is "threads" or "mpi".
        """
        n = self.getParam(prefix, 'count') or 1
        n_min = self.getParam(prefix, 'min')
        if (n_min is not None) and (n < n_min):
            n = n_min
            self.reason('{}_min={}', prefix, n_min)
        n_max = self.getParam(prefix, 'max')
        if (n_max is not None) and (n_max < n):
            n = n_max
            self.reason('{}_max={}', prefix, n_max)
        return n
