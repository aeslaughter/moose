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
        #params.add('executable')
        return params

    def execute(self, *args):

        exe = '/Users/slauae/projects/moose/framework/contrib/exodiff/exodiff'


        kwargs = dict()
        kwargs['capture_output'] = True
        kwargs['encoding'] = 'utf-8'
        kwargs['check'] = True # raise exceptions

        rcode = 0
        for filename, gold_filename in self.pairs():
            cmd = [exe, filename, gold_filename]
            str_cmd = ' '.join(cmd)
            print('RUNNING EXODIFF:\n{0}\n{1}\n{0}'.format('-' * len(str_cmd), str_cmd))
            out = subprocess.run(cmd, **kwargs)
            sys.stdout.write(out.stdout)
            sys.stderr.write(out.stderr)
            rcode += out.returncode

        return int(rcode > 0)
