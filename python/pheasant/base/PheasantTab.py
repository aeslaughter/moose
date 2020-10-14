from PySide2 import QtWidgets, QtCore
import factory
from .PheasantPlugin import PheasantPluginArea

class PheasantTab(factory.MooseObject, QtWidgets.QMainWindow):


    @staticmethod
    def validParams():
        params = factory.MooseObject.validParams()
        params.add('title', vtype=str, doc="Title to display on the tab")
        return params

    def __init__(self, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        factory.MooseObject.__init__(self, **kwargs)

        self.__plugins = dict()

        #self.__status_bar = QtWidgets.QStatusBar()
        #self.setStatusBar(self.__status_bar)

    def plugins(self):
        for plugin in self.__plugins.values():
            yield plugin

    def addPlugin(self, name, plugin):
        plugin.setObjectName(name)
        self.__plugins[name] = plugin


        #plugin._Plugin__setStatusMessage.connect(self.__onSetStatusMessage)


        location = location or PheasantPluginArea.LEFT
        if location == PheasantPluginArea.CENTER:
            # TODO: Error if exists
            self.setCentralWidget(plugin)
        elif location == PheasantPluginArea.STATUS:
            # TODO: Error if exists
            self.setStatusBar(plugin)
        else:
            self.addDockWidget(location, plugin)

    #def getPlugin(self, name):
    #    return self.__plugins[name]


    #def __onSetStatusMessage(self, msg, timeout):
    #    print('MESSAGE:', msg)
    #    QtCore.QCoreApplication.processEvents()
    #    self.__status_bar.showMessage(msg, timeout)
        #QtCore.QCoreApplication.processEvents()
        #self.__application.processEvents()
