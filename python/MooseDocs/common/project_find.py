import subprocess

import MooseDocs
from . import exceptions

def project_find(filename, mincout=None, maxcount=None, exc=exceptions.MooseDocsException):

    matches = [fname for fname in MooseDocs.PROJECT_FILES if fname.endswith(filename)]

    #if mincount and len(matches) < mincount:
    #    msg =
    return matches
