from moosetools.moosetest.base import make_differ
from moosetools.moosetest.differs import ConsoleDiff

from .RunApp import RunApp

class RunException(RunApp):
    """
    Run MOOSE application and perform basic output checks.

    Direct replacement for legacy TestHarness RunException Tester object.
    """
    @staticmethod
    def validParams():
        params = RunApp.validParams()

        # TODO: Deprecated, use ConsoleDiffer options
        params.add('expect_err', vtype=str,
                   doc="A regular expression or literal string that must occur in the output.")
        params.add('expect_assert', vtype=str,
                   doc="A regular expression or literal string that must occur in the output.")
        params.add('match_literal', vtype=bool, default=False,
                   doc="When True the strings supplied to 'expect_err' or 'expect_assert' must match exactly.")
        return params

    def __init__(self, *args, **kwargs):
        RunApp.__init__(self, *args, **kwargs)

        # TODO: Deprecated, update to use ConsoleDiffer options
        if self.isParamValid('expect_err') and self.isParamValid('expect_assert'):
            raise RuntimeError("Either the 'expect_err' or 'expect_assert' parameter must be supplied, but not both.")
        elif (not self.isParamValid('expect_err')) and (not self.isParamValid('expect_assert')):
            raise RuntimeError("Either the 'expect_err' or 'expect_assert' parameter  must be supplied.")

        param_name = 'expect_err' if self.isParamValid('expect_err') else 'expect_assert'
        c_diff = self.getParam('differs')[0]
        c_diff.parameters().setValue('nonzero_exit_expected', True)
        if self.getParam('match_literal'):
            c_diff.parameters().setValue('text_in_stderr', self.getParam(param_name))
        else:
            c_diff.parameters().setValue('re_match_stderr', self.getParam(param_name))
