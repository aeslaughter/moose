from PySide2 import QtWidgets
class PeacockTab(QtWidgets.QMainWindow):

    def __init__(self, name, *args):
        super().__init__()
        self.setObjectName(name)

        self.__plugins = []
        for plugin in args:
            self.__plugins.append(plugin)
            self.addDockWidget(plugin.pluginLocation(), plugin)

    def __iter__(self):
        for plugin in self.__plugins:
            yield plugin
