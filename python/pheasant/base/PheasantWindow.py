from PySide2 import QtWidgets
import factory
from pheasant import utils
from .PheasantTab import PheasantTab

class PheasantWindow(QtWidgets.QMainWindow, factory.MooseObject):

    @staticmethod
    def validParams():
        params = factory.MooseObject.validParams()
        return params

    def __init__(self, config=None, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        factory.MooseObject.__init__(self, **kwargs)

        #self._menu_bar = QtWidgets.QMenuBar()#self.menuBar()
        #self._menu_bar.setNativeMenuBar(True)


        #self.__settings = QtCore.QSettings()

        self.setCentralWidget(QtWidgets.QTabWidget())

        self.__tabs = dict()


    def addTab(self, name, **kwargs):
        obj = PheasantTab(**kwargs)
        obj.setObjectName(name)
        self.__tabs[name] = obj
        title = obj.getParam('title') if obj.isParamValid('title') else name
        self.centralWidget().addTab(obj, title)
        return obj

    def tabs(self):
        for tab in self.__tabs.values():
            yield tab

    def show(self):
        self.__initialize()
        super().show()





    def __initialize(self):

        plugins = list()
        for tab in self.tabs():
            for plugin in tab.plugins():
                plugins.append(plugin)
        for p0 in plugins:
            for p1 in plugins:
                if p0 is not p1:
                    utils.connect_plugin(p0, p1)

        for p0 in plugins:
            utils.setup_plugin(p0)
            utils.init_state(p0)
            p0.update()



        """
        # TODO: Get the first menu item text to show up instead of 'python'
        menu = self._menu_bar.addMenu('Peacock')
        action = menu.addAction('Preferences')
        action.setObjectName('Preferences')
        core.connectPlugin(self, action)

        parser = argparse.ArgumentParser(description='Process some integers.')

        plugins = []
        for tab in self.__tabs.values():
            menu = self._menu_bar.addMenu(tab.objectName())
            for plugin in tab:
                plugins.append(plugin)
                #plugin.createCommandLineOptions(parser)
                #plugin.createMenuItems(menu)
                for name, mitem in plugin._Plugin__menu_items.items():
                    action = menu.addAction(mitem)
                    action.setObjectName(name)
                    core.connectPlugin(plugin, action)
                    #attr = getattr(plugin, '_on{}Triggered'.format(mitem.title()), None)
                    #if attr:
                    #    action.triggered.connect(attr)

                    #else:
                        #TODO: Exception if not found




                #plugin.createSettings(self._settings)

        options = parser.parse_args()
        for plugin in plugins:
            #plugin.createWidgets(options)
            core.setupPlugin(plugin)

        for plugin0 in plugins:
            for plugin1 in plugins:
                core.connectPlugin(plugin0, plugin1, False)
        """


    #def _onPreferencesTriggered(self, *args):
    #    print('_onPreferencesTriggered')
