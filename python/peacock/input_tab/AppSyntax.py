import sys
from PySide2 import QtCore, QtWidgets
from .. import base

import MooseDocs

#from peacock import base

class AppSyntax(base.PeacockPlugin):

    def __init__(self):
        super().__init__()

        self._search = QtWidgets.QTextEdit()

        self.setWidget(self._search)


    def _onExecutableChanged(self, exe):

        syntax = MooseDocs.tree.app_syntax(exe)


        print(syntax)
