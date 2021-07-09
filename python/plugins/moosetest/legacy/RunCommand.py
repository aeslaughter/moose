from moosetools import moosetest

class RunCommand(moosetest.runners.ExecuteCommand):
    """
    Direct replacement for legacy TestHarness RunCommand Tester object.
    """
    @staticmethod
    def validParams():
        params = moosetest.runners.ExecuteCommand.validParams()

        # TODO:
        params.add('required_python_packages')
        params.add('requirement')

        return params

    def __init__(self, *args, **kwargs):
        moosetest.runners.ExecuteCommand.__init__(self, *args, **kwargs)
