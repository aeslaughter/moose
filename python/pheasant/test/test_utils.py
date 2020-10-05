#!/usr/bin/env python3
from PySide2 import QtCore, QtWidgets
from pheasant import utils

class Plugin(QtCore.QObject):
    """Test Plugin for connect/setupPlugin functions"""

    publicSignal = QtCore.Signal(int)
    _protectedSignal = QtCore.Signal(int)

    def __init__(self, *args):
        super().__init__(*args)

        self.public_value = None
        self.protected_value = None
        self.button_clicked = False
        self.setup_button = False

        self._button = QtWidgets.QPushButton()

    def onPublicSignal(self, value):
        self.public_value = value

    def _onProtectSignal(self, value):
        # NOT USED, this is here to make sure it is not connected
        self.protected_value = value

    def _onButtonClicked(self, *args):
        self.button_clicked = True

    def _setupButton(self, qobject):
        self.setup_button = True


class TestConnectPlugin(utils.PheasantTestCase):
    """utils.connect_plugin"""

    def testPublic(self):

        btn0 = Plugin()
        btn1 = Plugin()

        # connect slots of btn0 to signals of btn1
        utils.connect_plugin(btn0, btn1)

        # public signal/slot connection
        self.assertEqual(btn0.public_value, None)
        self.assertEqual(btn1.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertEqual(btn1.protected_value, None)
        self.assertFalse(btn0.button_clicked)
        self.assertFalse(btn1.button_clicked)
        self.assertFalse(btn0.setup_button)
        self.assertFalse(btn1.setup_button)

        btn0.publicSignal.emit(1949) # should do  nothing
        btn1.publicSignal.emit(1980)

        self.assertEqual(btn0.public_value, 1980)
        self.assertEqual(btn1.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertEqual(btn1.protected_value, None)
        self.assertFalse(btn0.button_clicked)
        self.assertFalse(btn1.button_clicked)
        self.assertFalse(btn0.setup_button)
        self.assertFalse(btn1.setup_button)

    def testLocal(self):
        btn0 = Plugin()
        btn0._button.setObjectName('Button')

        # connect slots of btn0 to signals of btn1
        utils.connect_plugin(btn0, btn0._button, local=True)

        self.assertEqual(btn0.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertFalse(btn0.button_clicked) # this is being tested
        self.assertFalse(btn0.setup_button)

        btn0._button.clicked.emit()

        self.assertEqual(btn0.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertTrue(btn0.button_clicked) # this is being tested
        self.assertFalse(btn0.setup_button)

class TestSetupPlugin(utils.PheasantTestCase):
    """utils.setup_plugin"""
    def testBasic(self):
        btn0 = Plugin()

        self.assertEqual(btn0.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertFalse(btn0.button_clicked) # this
        self.assertFalse(btn0.setup_button)   # and this  is being tested

        utils.setup_plugin(btn0)
        self.assertEqual(btn0.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertFalse(btn0.button_clicked) # this
        self.assertTrue(btn0.setup_button)   # and this  is being tested

        btn0._button.clicked.emit()

        self.assertEqual(btn0.public_value, None)
        self.assertEqual(btn0.protected_value, None)
        self.assertTrue(btn0.button_clicked) # this
        self.assertTrue(btn0.setup_button)   # and this  is being tested

if __name__ == '__main__':
    import unittest
    unittest.main(module=__name__, verbosity=2)
