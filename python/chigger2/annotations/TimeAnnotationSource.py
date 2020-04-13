#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
#pylint: enable=missing-docstring

import datetime

from TextAnnotationSource import TextAnnotationSource

class TimeAnnotationSource(TextAnnotationSource):
    """
    Source for creating time stamps.
    """

    @staticmethod
    def validParams():
        """
        Return default options for this object.
        """
        opt = TextAnnotationSource.validParams()
        opt.add('time', 330667320, vtype=float, doc="The time to display, in seconds.")
        opt.add('prefix', 'Time:', vtype=str, doc="The text to display prior to the time string.")
        opt.add('suffix', None, vtype=str, doc="The text to display after the time string.")
        opt.add('timedelta', False, vtype=bool,
                doc="Format the time using the python datetime.timedelta")
        opt.set('position', (0.01, 0.01))
        opt.remove('text')
        return opt

    def update(self, **kwargs):
        """
        Converts timestamp to a text string for display. (override)
        """
        super(TimeAnnotationSource, self).update(**kwargs)

        # The time to display
        time = self.getParam('time')

        # Build the text string
        text = []
        if self.isParamValid('prefix'):
            text.append(self.getParam('prefix'))

        if self.isParamValid('timedelta') and self.getParam('timedelta'):
            t = datetime.timedelta(seconds=time)
            text.append(str(t))
        else:
            text.append(str(time))

        if self.isParamValid('suffix'):
            text.append(self.getParam('suffix'))

        self._vtkactor.GetTextProperty().Modified()
        self._vtkactor.SetInput(' '.join(text))
