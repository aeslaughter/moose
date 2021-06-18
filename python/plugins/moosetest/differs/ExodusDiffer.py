import os
import sys
import subprocess

from moosetools.moosetest.base import FileDiffer

class ExodusDiffer(FileDiffer):
    """
    Compares ExodusII files.

    TODO: Add this to moosetools. This will require either adding the 'exodiff' utility to contrib
          or creating a custom python based tool. We could possible use github.com/cpgr/pyexodiff
    """
    @staticmethod
    def validParams():
        params = FileDiffer.validParams()
        params.add('executable', vtype=str,
                   doc="The 'exodiff' executable to run, if not specified the version in MOOSE is used.")
        params.add('abs_zero', vtype=float, default=1e-10,
                   doc="Absolute zero cutoff used in exodiff comparisons.")
        params.add('rel_err', vtype=float, default=5.5e-6,
                   doc="Relative error value used in exodiff comparisons.")

        return params

    def execute(self, *args):

        exe = self.getParam('executable')
        if exe is None:
            MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
            exe = os.path.join(MOOSE_DIR, 'framework', 'contrib', 'exodiff', 'exodiff')
        exe = os.path.relpath(exe, os.getcwd())

        if not os.path.isfile(exe):
            msg = "The supplied 'exodiff' executable does not exist: {}"
            raise RuntimeError(msg.format(exe))

        # subprocess.run key/value arguments
        kwargs = dict()
        kwargs['capture_output'] = True
        kwargs['encoding'] = 'utf-8'
        kwargs['check'] = False # raise exceptions

        # exodiff executable command to run
        cmd = [exe,
               '-tolerance', str(self.getParam('rel_err')),
               '-Floor', str(self.getParam('abs_zero')),
               '-map',
               None, # created file
               None] # gold file

        # Perform comparison of all file pairings
        for filename, gold_filename in self.pairs():
            cmd[-2] = os.path.relpath(filename, os.getcwd())
            cmd[-1] = os.path.relpath(gold_filename, os.getcwd())
            str_cmd = ' '.join(cmd)
            print('RUNNING EXODIFF:\n{0}\n{1}\n{0}'.format('-' * len(str_cmd), str_cmd))
            out = subprocess.run(cmd, **kwargs)
            sys.stdout.write(out.stdout)
            sys.stderr.write(out.stderr)
            if out.returncode > 0:
                self.error("{} != {}", cmd[-2], cmd[-1])
