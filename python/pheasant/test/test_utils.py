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

class TestState(utils.PheasantTestCase):
    def testInitState(self):
        parent = QtWidgets.QWidget()

        utils.init_state(parent)

        self.assertEqual(parent.property('pheasant/getState'), list())
        self.assertEqual(parent.property('pheasant/setState'), list())
        self.assertEqual(parent.property('pheasant/currentState'), dict())

    def testRegisterState(self):
        parent = QtWidgets.QWidget()
        utils.init_state(parent)

        def check(qobject):
            """Direct comparison of the method doesn't work, so check the effect"""
            qobject.setText('foo')
            self.assertEqual(len(parent.property('pheasant/getState')), 1)
            func = parent.property('pheasant/getState')[0]
            self.assertEqual(func(), 'foo')
            self.assertEqual(qobject.text(), 'foo')

            self.assertEqual(len(parent.property('pheasant/setState')), 1)
            func = parent.property('pheasant/setState')[0]
            func('bar')
            self.assertEqual(qobject.text(), 'bar')

        edit = QtWidgets.QLineEdit()
        utils.register_state(parent, edit, 'text')
        check(edit)

        edit2 = QtWidgets.QLineEdit()
        utils.register_state(parent, edit2, ('text', 'setText'))
        check(edit2)

        edit3 = QtWidgets.QLineEdit()
        utils.register_state(parent, edit3, (edit3.text, lambda x: edit3.setText(x)))
        check(edit3)

        with self.assertRaises(TypeError) as e:
            utils.register_state(parent, edit3, 1)
        self.assertIn('single string or a tuple with two items', str(e.exception))

        with self.assertRaises(TypeError) as e:
            utils.register_state(parent, edit3, (1,2,3))
        self.assertIn('single string or a tuple with two items', str(e.exception))

        with self.assertRaises(TypeError) as e:
            utils.register_state(parent, edit3, (1,2))
        self.assertIn('get name/method must', str(e.exception))

        with self.assertRaises(TypeError) as e:
            utils.register_state(parent, edit3, (edit3.text, 2))
        self.assertIn('set name/method must', str(e.exception))

    def testSaveLoadState(self):
        parent = QtWidgets.QWidget()
        utils.init_state(parent)
        edit = QtWidgets.QLineEdit()
        utils.register_state(parent, edit, 'text')

        edit.setText('foo')
        self.assertEqual(edit.text(), 'foo')
        utils.save_state(parent, 'A')

        edit.setText('bar')
        self.assertEqual(edit.text(), 'bar')
        utils.save_state(parent, 'B')

        utils.load_state(parent, 'A')
        self.assertEqual(edit.text(), 'foo')

        utils.load_state(parent, 'B')
        self.assertEqual(edit.text(), 'bar')

        utils.load_state(parent, 'A')
        self.assertEqual(edit.text(), 'foo')

class TestAddLabelWidget(utils.PheasantTestCase):

    def setUp(self):
        super().setUp()
        self._parent = QtWidgets.QWidget()
        self._parent.setLayout(QtWidgets.QVBoxLayout())
        self._layout = self._parent.layout()
        self._edit = QtWidgets.QLineEdit()

    def testWidgetThenLabelHoriz(self):
        utils.add_labeled_widget(self._layout, self._edit, 'label')
        self.assertEqual(self._layout.count(), 1)
        self.assertEqual(self._layout.itemAt(0).count(), 2)

    def testLabelThenWidgetHoriz(self):
        utils.add_labeled_widget(self._layout, 'label', self._edit)
        self.assertEqual(self._layout.count(), 1)
        self.assertEqual(self._layout.itemAt(0).count(), 2)

    def testWidgetThenLabelVertical(self):
        utils.add_labeled_widget(self._layout, self._edit, 'label', stretch=1, vertical=True)
        self.assertEqual(self._layout.count(), 1)
        self.assertEqual(self._layout.itemAt(0).count(), 3)

    def testLabelThenWidgetVertical(self):
        utils.add_labeled_widget(self._layout, 'label', self._edit, vertical=True)
        self.assertEqual(self._layout.count(), 1)
        self.assertEqual(self._layout.itemAt(0).count(), 2)

if __name__ == '__main__':
    import unittest
    unittest.main(module=__name__, verbosity=2)
