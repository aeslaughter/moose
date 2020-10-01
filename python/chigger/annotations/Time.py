#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import datetime
from .TextBase import TextBase

class Time(TextBase):
    """
    Source for creating time stamps.
    """

    @staticmethod
    def validOptions():
        """
        Return default options for this object.
        """
        opt = TextBase.validOptions()
        opt.add('days', vtype=(int, float), default=0, doc="The number of days.")
        opt.add('weeks', vtype=(int, float), default=0, doc="The number of weeks.")
        opt.add('hours', vtype=(int, float), default=0, doc="The number of hours.")
        opt.add('minutes', vtype=(int, float), default=0, doc="The number of minutes.")
        opt.add('seconds', vtype=(int, float), default=0, doc="The number of seconds.")
        opt.add('microseconds', vtype=(int, float), default=0, doc="The number of microseconds.")
        opt.add('milliseconds', vtype=(int, float), default=0, doc="The number of milliseconds.")

        opt.set('position', (0.01, 0.01))
        opt.remove('text')
        return opt

    def _onRequestInformation(self, *args):
        """
        Converts timestamp to a text string for display. (override)
        """
        td = datetime.timedelta(**{k:self.getOption(k) for k in ['days', 'weeks', 'hours', 'minutes', 'seconds', 'microseconds', 'milliseconds']})
        self._vtkactor.SetInput(str(td))
        TextBase._onRequestInformation(self, *args)
