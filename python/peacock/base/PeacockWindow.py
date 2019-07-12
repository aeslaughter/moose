import argparse
from PySide2 import QtWidgets, QtCore
from .PeacockTab import PeacockTab

class PeacockWindow(QtWidgets.QMainWindow):

    def __init__(self, *args):
        super().__init__()

        self._parser = argparse.ArgumentParser(description='Process some integers.')
        self._options = self._parser.parse_args()

        # TODO: For linux make menu bar part of window
        self._menu_bar = QtWidgets.QMenuBar()#self.menuBar()
        self._menu_bar.setNativeMenuBar(True)

        self._settings = QtCore.QSettings()

        self.setCentralWidget(QtWidgets.QTabWidget())

        """
        plugins = []
        for tab in args:
            menu = self._menu_bar.addMenu(tab.objectName())
            self.centralWidget().addTab(tab, tab.objectName())
            for plugin in tab:
                plugins.append(plugin)
                plugin.createCommandLineOptions(parser)
                plugin.createMenuItems(menu)
                plugin.createSettings(self._settings)

        options = parser.parse_args()
        for plugin in plugins:
            plugin.createWidgets(options)
            self.__setupPlugin(plugin)

        for plugin0 in plugins:
            for plugin1 in plugins:
                self.__connectPlugin(plugin0, plugin1, False)
        """
    def addTab(self, tab, *args):

        if isinstance(tab, str):
            tab = PeacockTab(tab, *args)

        menu = self._menu_bar.addMenu(tab.objectName())
        self.centralWidget().addTab(tab, tab.objectName())
        for plugin in tab:
            plugin.createCommandLineOptions(self._parser)
            plugin.createMenuItems(menu)
            plugin.createSettings(self._settings)



    def show(self):


        plugins = list()
        for index in range(self.centralWidget().count()):
            tab = self.centralWidget().widget(index)
            for plugin in tab:
                plugins.append(plugin)
                plugin.createWidgets(self._options)
                self.__setupPlugin(plugin)

        for plugin0 in plugins:
            for plugin1 in plugins:
                self.__connectPlugin(plugin0, plugin1, False)


        super().show()
    #def __iter__(self):
    #    for tab in self.__tabs:
    #        for plugin in tab:
    #            yield plugin


    @staticmethod
    def __connectPlugin(plugin, qobject, local=True):
        name = qobject.objectName()

        for key in dir(qobject):
            attr = getattr(qobject, key)
            # isinstance(QtCore.Signal)
            if attr.__class__.__name__ == 'SignalInstance':
                if local:
                    callback = getattr(plugin, '_on{}{}'.format(name, key.title()), None)
                else:
                    callback = getattr(plugin, 'on{}'.format(key.title()), None)

                if callback:
                    attr.connect(callback)

    @staticmethod
    def __setupPlugin(plugin):
        widgets = []
        for key, value in plugin.__dict__.items():
            if isinstance(value, QtWidgets.QWidget):
                widgets.append(value)
                if not value.objectName():
                    value.setObjectName(key.strip('_').title())

        for widget in widgets:
            setup_name = '_setup{}'.format(widget.objectName())
            setup_func = getattr(plugin, setup_name, None)
            if setup_func:
                setup_func(widget)

            PeacockWindow.__connectPlugin(plugin, widget)
