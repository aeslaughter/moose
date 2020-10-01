#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import os
from .Image import Image

class Logo(Image):
    """
    A helper version of Image for displaying logos from chigger/logos directory
    """
    @staticmethod
    def validOptions():
        """
        Return the default options for this object.
        """
        opt = Image.validOptions()
        opt.add('logo', vtype=str, required=True, doc="The name of the logo (e.g., 'moose').")
        return opt

    def __init__(self, *args, **kwargs):
        Image.__init__(self, *args, **kwargs)
        self._location = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logos'))

    def _onRequestInformation(self, *args):
        self.setOption('filename', os.path.join(self._location, '{}.png'.format(self.getOption('logo').lower())))
        Image._onRequestInformation(self, *args)
