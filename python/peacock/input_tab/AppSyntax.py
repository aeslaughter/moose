import sys
from PySide2 import QtCore, QtWidgets
from .. import base

from MooseDocs import tree

#from peacock import base

class AppSyntax(base.PeacockPlugin):

    def __init__(self):
        super().__init__()

        self._search = QtWidgets.QTextEdit()

        self.setWidget(self._search)


    def _onExecutableChanged(self, exe):



        exe = "/Users/slauae/projects/moose/test/moose_test-devel"
        syntax = tree.app_syntax(exe)


        print(syntax)
