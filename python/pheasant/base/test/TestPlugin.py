from PySide2 import QtWidgets, QtCore
import pheasant

class TestPlugin(pheasant.PheasantPlugin):
    pressed = QtCore.Signal(str)

    @staticmethod
    def validParams():
        params = Pheasant.PheasantPlugin.validParams()
        return params

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._button = QtWidgets.QPushButton("Button 1")
        self.setWidget(self._button)

    def _onButtonClicked(self, args):
        self.setStatus('TestPlugin::_onButtonClicked')
        self.pressed.emit("Pressed Button 1")
