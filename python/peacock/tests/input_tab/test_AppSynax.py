#!/usr/bin/env python
import sys
from PySide2 import QtCore, QtWidgets
from peacock import base, input_tab



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    #window = Peacock()
    window = base.PeacockWindow()
    syntax = input.AppSyntax()
    window.addTab('AppSyntax', syntax)

    window.show()

    exe = '/Users/slauae/projects/moose/test/moose_test-devel'
    syntax._onExecutableChanged(exe)


    # Enter Qt application main loop
    app.exec_()
    sys.exit()
