from moosetools import moosetest

class RunCommand(moosetest.runners.RunCommand):
    """
    Direct replacement for legacy TestHarness RunCommand Tester object.
    """
    @staticmethod
    def validParams():
        params = moosetest.runners.RunCommand.validParams()

        # TODO:
        params.add('required_python_packages')

        return params

    def __init__(self, *args, **kwargs):
        moosetest.runners.RunCommand.__init__(self, *args, **kwargs)
