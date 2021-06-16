from moosetools.moosetest.base import make_differ
from moosetools.moosetest.differs import ConsoleDiffer

from ..runners import MOOSEAppRunner
from ..differs import PETScJacobianDiffer

class RunApp(MOOSEAppRunner):
    """
    Run MOOSE application and perform basic output checks.

    Direct replacement for legacy TestHarness RunApp Tester object.
    """
    @staticmethod
    def validParams():
        params = MOOSEAppRunner.validParams()
        params.add('absent_out', vtype=str,
                   doc="Ensure that the supplied text is not found the output text.")
        return params

    def __init__(self, *args, **kwargs):
        MOOSEAppRunner.__init__(self, *args, **kwargs)

        # Get parameters from the Runner that should be applied to the Differ
        kwargs = dict()
        kwargs['base_dir'] = self.getParam('base_dir')
        kwargs['re_not_match'] = self.getParam('absent_out')

        # Create and add the Differ
        controllers = self.getParam('_controllers')
        c_differ = make_differ(ConsoleDiffer, controllers, name='consolediff', **kwargs)
        self.parameters().setValue('differs', (c_differ,))
