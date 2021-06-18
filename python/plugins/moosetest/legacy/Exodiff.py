from moosetools.moosetest.base import make_differ
from .RunApp import RunApp
from ..differs import ExodusDiffer

class Exodiff(RunApp):
    """
    Run MOOSE application and compare Exodus files.

    Direct replacement for legacy TestHarness Exodiff Tester object.
    """
    @staticmethod
    def validParams():
        params = RunApp.validParams()
        params.add('exodiff', array=True, vtype=str,
                   doc="ExodusII file(s) to compare with counterpart in 'gold' directory.")

        # Add parameters from the Differ object
        differ_params = ExodusDiffer.validParams()
        params.append(differ_params, 'abs_zero', 'rel_err')

        return params

    def __init__(self, *args, **kwargs):
        RunApp.__init__(self, *args, **kwargs)

        # Get parameters from the Runner that should be applied to the Differ
        kwargs = dict()
        kwargs['file_names'] = self.getParam('exodiff')
        kwargs['abs_zero'] = self.getParam('abs_zero')
        kwargs['rel_err'] = self.getParam('rel_err')

        # Create and add the Differ
        controllers = self.getParam('_controllers')
        exo_differ = make_differ(ExodusDiffer, controllers, name='exodiff', **kwargs)

        differs = list(self.getParam('differs'))
        self.parameters().setValue('differs', tuple([exo_differ, *differs]))
