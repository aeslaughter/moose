from PySide2 import QtWidgets
import parameters

class PheasantWidget(object):

    @staticmethod
    def validParams():
        params = parameters.InputParameters()
        return params


    def __init__(self):
        #assert isinstance(self, QtWidgets.QWidget), 'Object must be a QWidget object'.format(self.__class__.__name__)
