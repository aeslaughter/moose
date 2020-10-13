import logging
import unittest
from PySide2 import QtCore, QtWidgets


WIDGET_SETTINGS_CACHE = dict()
WIDGET_SETTINGS_CACHE[QtWidgets.QLineEdit] = [('text', 'setText'),
                                              ('styleSheet', 'setStyleSheet')]
#WIDGET_SETTINGS_CACHE[QtWidgets.QCheckBox] = [(QtWidgets.QCheckBox.isChecked, QtWidgets.QCheckBox.setChecked)]
#WIDGET_SETTINGS_CACHE[QtWidgets.QComboBox] = [(QtWidgets.QComboBox.currentText,
#                                               lambda s, t: QtWidgets.QComboBox.setCurrentIndex(s, QtWidgets.QComboBox.findText(s, t)))]
#WIDGET_SETTINGS_CACHE[QtWidgets.QSlider] = [(QtWidgets.QSlider.sliderPosition, QtWidgets.QSlider.setSliderPosition)]
#WIDGET_SETTINGS_CACHE[QtWidgets.QGroupBox] = [(QtWidgets.QGroupBox.isChecked, QtWidgets.QGroupBox.setChecked)]
#WIDGET_SETTINGS_CACHE[QtWidgets.QSpinBox] = [(QtWidgets.QSpinBox.value, QtWidgets.QSpinBox.setValue)]
#WIDGET_SETTINGS_CACHE[QtWidgets.QDoubleSpinBox] = [(QtWidgets.QDoubleSpinBox.value, QtWidgets.QDoubleSpinBox.setValue)]

def connect_plugin(plugin, qobject, local=False):
    """
    Auto connect the slots of the plugin to the signals of the qobject

    Inputs:
        plugin[QObject]: An object that has potential slots
        qobject[QObject]: An object that is emitting signals to be connect the the plugin slots
        local[bool]: When True the connecting is changed to "local" operation, which is intended
                     for connecting QObjects that are children of the plugin. The object name of the
                     supplied QObject must be defined, see setup_plugin.

    """
    for key in [k for k in dir(qobject) if not k.startswith('_')]:
        attr = getattr(qobject, key)
        if isinstance(attr, QtCore.SignalInstance):
            title = '{}{}'.format(key[0].upper(), key[1:])
            slot_name = '_on{}{}'.format(qobject.objectName(), title) if local else 'on{}'.format(title)
            callback = getattr(plugin, slot_name, None)
            if callback:
                attr.connect(callback)

def setup_plugin(plugin):
    """
    Setup the plugin for operation.

    (1) Set the name for all QObjects as follows:
        self._this_button => ThisButton

    (2) Call the setup function for the QObjects:
        self._setupThisButton(self, qobject)

    (3) Connect the slots of the plugin with the signals of the member QObjects using the
        connect_plugin function above
    """

    qobjects = []
    for key, value in plugin.__dict__.items():
        if isinstance(value, QtCore.QObject):
            name = ''.join(k.title() for k in key.split('_'))
            value.setObjectName(name)
            qobjects.append(value)

    for qobject in qobjects:
        setup_name = '_setup{}'.format(qobject.objectName())
        setup_func = getattr(plugin, setup_name, None)
        if setup_func:
            setup_func(qobject)

        connect_plugin(plugin, qobject, local=True)

def init_state(parent):
    """
    Create storage for load/storing state information with Qt property system.

    Inputs:
        parent[QObject]: The object that will store state of child objects
    """
    parent.setProperty('pheasant/getState', list())
    parent.setProperty('pheasant/setState', list())
    parent.setProperty('pheasant/currentState', dict())

def register_state(parent, widget, *args):
    """
    Register child objects for load/store of state information.

    init_state(parent) should be called prior to this method.

    Inputs:
        parent[QObject]: The object that will store state of child objects
        widget[QObject]: A child object for which state will be stored
        args: A list of strings or tuples that provide the setter/getter functions

    Example:

        init_state(parent, widget, 'text', ('checked', 'setChecked'), (widget.clicked, widget.setClicked))

    """
    getters = list()
    setters = list()

    for arg in args:
        if isinstance(arg, str):
            get_name = arg
            set_name = 'set{}'.format(get_name.title())
        elif isinstance(arg, tuple) and (len(arg) == 2):
            get_name = arg[0]
            set_name = arg[1]
        else:
            raise TypeError("The supplied arguments must be a single string or a tuple with two items (str or callable): ".format(arg))

        if isinstance(get_name, str):
            getters.append(getattr(widget, get_name))
        elif callable(get_name):
            getters.append(get_name)
        else:
            raise TypeError("The supplied get name/method must be a 'str' or callable: {}".format(get_name))

        if isinstance(set_name, str):
            setters.append(getattr(widget, set_name))
        elif callable(set_name):
            setters.append(set_name)
        else:
            raise TypeError("The supplied set name/method must be a 'str' or callable: {}".format(set_name))

    prop = parent.property('pheasant/getState')
    prop += getters
    parent.setProperty('pheasant/getState', getters)

    prop = parent.property('pheasant/setState')
    prop += setters
    parent.setProperty('pheasant/setState', setters)

def save_state(parent, key):
    """
    Save the QObject state with the given key name.

    Inputs:
        parent[QObject]: The object that will store state of child objects
        key[str]: The name of the state
    """
    getters = parent.property('pheasant/getState'.format(key))
    state = list()
    for attr in getters:
        state.append(attr())
    data = parent.property('pheasant/currentState')
    data[key] = state
    parent.setProperty('pheasant/currentState', data)

def load_state(parent, key):
    """
    Load the QObject state with the given key name.

    Inputs:
        parent[QObject]: The object that will store state of child objects
        key[str]: The name of the state
    """
    state = parent.property('pheasant/currentState')[key]
    setters = parent.property('pheasant/setState')
    for value, attr in zip(state, setters):
        attr(value)

def addLabeledWidget(parent, arg0, arg1, stretch=None):
    """
    Function for creating a widget with a text label.

    Inputs:
        parent[QWidget]: The parent widget
        arg0[str|QWidget]: The label or the widget
        arg1[str|QWidget]: The label or the widget, must be the other type from arg0
        stretch[int]: Location to add stretch

    """
    layout = QtWidgets.QHBoxLayout()
    parent.layout().addLayout(layout)
    if isinstance(arg0, str):
        label = QtWidgets.QLabel(arg0)
        layout.addWidget(label)
        layout.addWidget(arg1)
    else:
        label = QtWidgets.QLabel(arg1)
        layout.addWidget(argo)
        layout.addWidget(label)

    if stretch is not None:
        layout.insertStretch(stretch)

class PheasantTestCase(unittest.TestCase):
    """
    Helper object for performing unit testing of Qt objects
    """
    APPLICATION = None

    def setUp(self):
        if PheasantTestCase.APPLICATION is None:
            PheasantTestCase.APPLICATION = QtWidgets.QApplication()
        self._app = PheasantTestCase.APPLICATION

    def tearDown(self):
        del self._app
