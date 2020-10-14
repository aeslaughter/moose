import parameters

class MooseObject(object):

    @staticmethod
    def validParams():
        params = parameters.InputParameters()
        params.add('name', vtype=str, doc="The name of the object.")
        return params

    def __init__(self, **kwargs):
        super().__init__()
        self.__parameters = getattr(self.__class__, 'validParams')()
        self.__parameters.update(**kwargs)
        self.__parameters.validate()

    def name(self):
        """
        Return the name of the object.
        """
        return self.__parameters.get('name')

    def isParamValid(self, pname):
        """
        Return True if the parameter exists and is not None.

        Inputs:
            pname[str]: Name of the parameter to check
        """
        return self.__parameters.isValid(pname)

    def getParam(self, pname):
        """
        Return the value of a parameter.

        Inputs:
            pname[str]: Name of the parameter to check
        """
        return self.__parameters.get(pname)
