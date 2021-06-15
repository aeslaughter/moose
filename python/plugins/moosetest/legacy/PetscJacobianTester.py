from moosetools.moosetest.base import make_differ
from ..runners import MOOSEAppRunner
from ..differs import PETScJacobianDiffer

class PetscJacobianTester(MOOSEAppRunner):
    """
    Run MOOSE application with PETSc options for performing Jacobian checks.

    Direct replacement for legacy TestHarness PetscJacobianTester Tester object.
    """

    @staticmethod
    def validParams():
        params = MOOSEAppRunner.validParams()

        # Add parameters from the Differ object
        differ_params = PETScJacobianDiffer.validParams()
        params.append(differ_params, 'ratio_tol', 'difference_tol', 'only_final_jacobian')

        params.add('run_sim', default=False, doc="Whether to actually run the simulation, testing the Jacobian "
                                                 "at every non-linear iteration of every time step. This is only "
                                                 "relevant for petsc versions >= 3.9.")
        params.add('turn_off_exodus_output', default=True, doc="Whether to set exodus=false in Outputs")
        return params

    def __init__(self, *args, **kwargs):
        MOOSEAppRunner.__init__(self, *args, **kwargs)

        # Get parameters from the Runner that should be applied to the Differ
        kwargs = dict()
        kwargs['base_dir'] = self.getParam('base_dir')
        kwargs['ratio_tol'] = self.getParam('ratio_tol')
        kwargs['difference_tol'] = self.getParam('difference_tol')
        kwargs['only_final_jacobian'] = self.getParam('only_final_jacobian')

        # Create and add the Differ
        controllers = self.getParam('_controllers')
        jac_differ = make_differ(PETScJacobianDiffer, controllers, name='jacobiandiff', **kwargs)
        self.parameters().setValue('differs', (jac_differ,))


    def execute(self, *args, **kwargs):
        """
        Update the 'cli_args' parameter to include the PETSc options needed for Jacobian testing.
        """

        # Extend 'cli_args' parameter to run PETSc as needed
        cli_args = list(self.getParam('cli_args'))
        if self.getParam('turn_off_exodus_output'):
            cli_args += ['Outputs/exodus=false']

        cli_args += ['-snes_test_jacobian', '-snes_force_iteration']
        if not self.getParam('run_sim'):
            cli_args += ['-snes_type', 'ksponly', '-ksp_type', 'preonly', '-pc_type', 'none', '-snes_convergence_test', 'skip']

        self.parameters().setValue('cli_args', tuple(cli_args))
        return MOOSEAppRunner.execute(self, *args, **kwargs)
