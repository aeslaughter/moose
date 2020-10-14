import enum
from PySide2 import QtWidgets, QtCore
import factory

class PheasantPluginArea(enum.Enum):
    NONE = QtCore.Qt.NoDockWidgetArea
    LEFT = QtCore.Qt.LeftDockWidgetArea
    RIGHT = QtCore.Qt.RightDockWidgetArea
    TOP = QtCore.Qt.TopDockWidgetArea
    BOTTOM = QtCore.Qt.BottomDockWidgetArea
    CENTER = -1
    STATUS = -2

class PheasantPlugin(QtWidgets.QDockWidget, factory.MooseObject):

    @staticmethod
    def validParams():
        params = factory.MooseObject.validParams()
        params.add('dockable', default=False, vtype=bool, doc="Enable the ability to dock/undock plugin")
        params.add('location', default=PheasantPluginArea.LEFT, vtype=PheasantPluginArea,
                   doc="Area within tab to place plugin")
        return params

    def __init__(self, **kwargs):
        QtWidgets.QDockWidget.__init__(self)
        factory.MooseObject.__init__(self, **kwargs)
        #assert isinstance(self, QtWidgets.QWidget), 'Object must be a QWidget object'.format(self.__class__.__name__)


    def update(self):
        pass
        #self.setFeatures(self.getParam('dockable'))
