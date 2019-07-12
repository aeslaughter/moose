from PySide2 import QtWidgets, QtCore

class PeacockPlugin(QtWidgets.QDockWidget):
    LEFT = QtCore.Qt.LeftDockWidgetArea
    RIGHT = QtCore.Qt.RightDockWidgetArea
    TOP = QtCore.Qt.TopDockWidgetArea
    BOTTOM = QtCore.Qt.BottomDockWidgetArea
    #CENTER =

    def createCommandLineOptions(self, parser):
        pass

    def createWidgets(self, options):
        pass

    def createMenuItems(self, menu):
        pass

    def createSettings(self, settings):
        #TODO
        pass

    def __init__(self, location=None):
        super().__init__()
        self.__location = None
        self.setPluginLocation(location or PeacockPlugin.LEFT)

    #def get(self, key, None):
     #   return self.__settings

    #def initialize(self, options):
     #   self.createWidgets(options)
     #   self.__setup()

    def pluginLocation(self):
        return self.__location

    def setPluginLocation(self, location):
        self.__location = location
