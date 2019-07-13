#!/usr/bin/env python

import sys
from PySide2 import QtCore, QtWidgets

import base

class TestPlugin(base.PeacockPlugin):

    pressed = QtCore.Signal(str)

    def createWidgets(self, options):

        self._button = QtWidgets.QPushButton("Button 1")
        self.setWidget(self._button)

    def _onButtonClicked(self, args):
        print('TestPlugin:HELLO')
        self.pressed.emit("Pressed Button 1")


class TestPlugin2(base.PeacockPlugin):

    def createMenuItems(self, menu):
        menu.addAction('Test')

    def createWidgets(self, options):

        self._button = QtWidgets.QPushButton("Button 2")
        self.setWidget(self._button)

    def _setupButton(self, qobject):
        pass
        #qobject.clicked.connect(self._callbackButton)

    def _onButtonClicked(self, *args):
        print('TestPlugin2:HELLO')
#    pass

    def onPressed(self, incoming):
        print(incoming, "from", '2')


if __name__ == '__main__':

    # Create a Qt application
    app = QtWidgets.QApplication(sys.argv)

    #window = Peacock()
    window = base.PeacockWindow()
    window.addTab('One', TestPlugin())
    window.addTab('Two', TestPlugin2(), TestPlugin2())

    window.show()
    # Enter Qt application main loop
    app.exec_()
    sys.exit()
