import collections
from moosedown import common

class Grammer(object):
    """
    Defines a generic Grammer that contains the Token objects necessary to build an
    abstract syntax tree (AST). This class defines the order that the tokens will be
    applied to the Lexer object and the associated regular expression that define the
    text associated with the Token object.
    """

    #: Container for information required for creating a Token object.
    Pattern = collections.namedtuple('Pattern', 'name regex function')

    def __init__(self):
        self.__patterns = common.Storage(Grammer.Pattern)

    def add(self, name, regex, function, location=-1):
        """
        Method for adding a Token definition to the Grammer object.

        Inputs:
            name[str]: The name of the grammer definition, this is utilized for
                       ordering of the definitions.
            regex[re]: A compiled re object that defines what text the token should
                       be associated.
            function[function]: A function that accepts a regex match object as input and
                                returns a token object.
            location[int or str]:  (Optional) In the case of an int type, this is an
                                   index indicating the location in the list of definitions
                                   to insert. In the case of a str type the following syntax
                                   is support to insert definitions relative to other
                                   definitions.
                                        '_begin': Insert the new definition at the beginning
                                                  of the list of definitions, this is the same
                                                  as using an index of 0.
                                        '_end': Append the new definition at the end of the list
                                                of definitions (this is the default).
                                        '<foo': Insert the new definition before the definition
                                                named 'foo'.
                                        '>foo': Insert the new definition after the definition
                                                named 'foo'.
        """
        self.__patterns.add(name,
                            Grammer.Pattern(name=name, regex=regex, function=function),
                            location)

    def __getitem__(self, key):
        """
        Return the pattern for a given key.
        """
        return self.__patterns[key]

    def __iter__(self):
        """
        """
        for obj in self.__patterns:
            yield obj

    #def __createToken(self, obj, *args):
    #    return obj()
