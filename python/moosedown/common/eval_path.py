"""Tool for applying environment variable to paths."""

import os
import re

def eval_path(path):
    """
    Import envirornment variables into paths.

    Inputs:
        path[str]: Path containing environment variable: e.g., ${MOOSE_DIR}/python
    """
    def sub(match):
        env = match.group('env')
        if env in os.environ:
            return os.environ[env]
        return match.group()

    return re.sub(r'\$\{(?P<env>.*?)\}', sub, path)
