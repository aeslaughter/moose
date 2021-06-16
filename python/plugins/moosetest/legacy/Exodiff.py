from moosetools.moosetest.base import make_differ
from ..runners import MOOSEAppRunner
from ..differs import ExodusDiffer

class Exodiff(MOOSEAppRunner):
    """
    Run MOOSE application and compare Exodus files.

    Direct replacement for legacy TestHarness Exodiff Tester object.
    """
    @staticmethod
    def validParams():
        params = MOOSEAppRunner.validParams()
        params.add('exodiff', array=True, vtype=str,
                   doc="ExodusII file(s) to compare with counterpart in 'gold' directory.")

        # Add parameters from the Differ object
        differ_params = ExodusDiffer.validParams()
        params.append(differ_params, 'abs_zero', 'rel_err')

        return params

    def __init__(self, *args, **kwargs):
        MOOSEAppRunner.__init__(self, *args, **kwargs)

        # Get parameters from the Runner that should be applied to the Differ
        kwargs = dict()
        kwargs['filenames'] = self.getParam('exodiff')
        kwargs['base_dir'] = self.getParam('base_dir')

        # Create and add the Differ
        controllers = self.getParam('_controllers')
        exo_differ = make_differ(ExodusDiffer, controllers, name='exodiff', **kwargs)
        self.parameters().setValue('differs', (exo_differ,))
