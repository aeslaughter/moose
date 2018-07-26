#!/usr/bin/env python2
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from PyQt5 import QtWidgets, QtCore
from peacock import PeacockApp
from peacock.utils import Testing
import os

class TestExodusColorbarVisible(Testing.PeacockImageTestCase):
    qapp = QtWidgets.QApplication([])
    INPUT_FILE = "../../common/transient.i"
    def setUp(self):
        """
        Creates the peacock application.
        """
        Testing.setupTestCache(self.__class__)
        args = ["-size", "1024", "768", "-i", self.INPUT_FILE, "-e", Testing.find_moose_test_exe()]
        working_dir = os.getcwd()
        self._app = PeacockApp.PeacockApp(args, self.qapp)
        os.chdir(working_dir)
        self._window = self._app.main_widget.tab_plugin.ExodusViewer.currentWidget().VTKWindowPlugin
        Testing.set_window_size(self._window)
        Testing.remove_file('peacock_run_exe_tmp_out.e')

    def selectTab(self, tab):
        """
        Helper function for toggling tabs.
        """
        self._app.main_widget.tab_plugin.setCurrentWidget(tab)
        self._app.main_widget.tab_plugin.currentChanged.emit(self._app.main_widget.tab_plugin.currentIndex())
        Testing.process_events(t=1)

    def execute(self):
        """
        Helper for running executable.
        """
        execute = self._app.main_widget.tab_plugin.ExecuteTabPlugin
        execute.ExecuteRunnerPlugin.runClicked()
        Testing.process_events(t=5)

    def testMultipleRun(self):
        exodus = self._app.main_widget.tab_plugin.ExodusViewer
        plugin = exodus.currentWidget().ColorbarPlugin
        self.selectTab(exodus)
        self.execute()

        plugin.ColorBarToggle.setChecked(QtCore.Qt.Unchecked)
        plugin.ColorBarToggle.stateChanged.emit(QtCore.Qt.Unchecked)
        self.assertFalse(plugin.ColorBarToggle.isChecked())
        self.assertImage('multipleRun.png')

        #self.selectTab(exodus)
        self.execute()
        self.assertFalse(plugin.ColorBarToggle.isChecked())
        self.assertImage('multipleRun.png')

if __name__ == '__main__':
    Testing.run_tests()
